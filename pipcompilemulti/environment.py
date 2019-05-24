"""Environment class"""

import os
import re
import logging
import subprocess

from .options import OPTIONS
from .dependency import Dependency


logger = logging.getLogger("pip-compile-multi")


class Environment(object):
    """requirements file"""

    RE_REF = re.compile(r'^(?:-r|--requirement)\s*(?P<path>\S+).*$')

    def __init__(self, name, ignore=None, forbid_post=False, add_hashes=False):
        """
        name - name of the environment, e.g. base, test
        ignore - set of package names to omit in output
        """
        self.name = name
        self.ignore = ignore or {}
        self.forbid_post = forbid_post
        self.add_hashes = add_hashes
        self.packages = {}
        self._outfile_pkg_names = None

    def create_lockfile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        Then fix it.
        """
        process = subprocess.Popen(
            self.pin_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            self.fix_lockfile()
        else:
            logger.critical("ERROR executing %s", ' '.join(self.pin_command))
            logger.critical("Exit code: %s", process.returncode)
            logger.critical(stdout.decode('utf-8'))
            logger.critical(stderr.decode('utf-8'))
            raise RuntimeError("Failed to pip-compile {0}".format(self.infile))

    def maybe_create_lockfile(self):
        """
        Write recursive dependencies list to outfile unless the goal is to
        upgrade specific package(s) which don't already
        appear. Populate package ignore set in either case and return
        boolean indicating whether outfile was written.
        """
        if OPTIONS['upgrade_packages'] and not any(
                self.is_package_in_outfile(p)
                for p in OPTIONS['upgrade_packages']):
            self.fix_lockfile()  # populate ignore set
            return False

        self.create_lockfile()
        return True

    @classmethod
    def parse_references(cls, filename):
        """
        Read filename line by line searching for pattern:

        -r file.in
        or
        --requirement file.in

        return set of matched file names without extension.
        E.g. ['file']
        """
        references = set()
        for line in open(filename):
            matched = cls.RE_REF.match(line)
            if matched:
                reference = matched.group('path')
                reference_base = os.path.splitext(reference)[0]
                references.add(reference_base)
        return references

    @property
    def infile(self):
        """Path of the input file"""
        return os.path.join(OPTIONS['base_dir'],
                            '{0}.{1}'.format(self.name, OPTIONS['in_ext']))

    @property
    def outfile(self):
        """Path of the output file"""
        return os.path.join(OPTIONS['base_dir'],
                            '{0}.{1}'.format(self.name, OPTIONS['out_ext']))

    def is_package_in_outfile(self, pkg):
        """Is specified package name already in the outfile?"""
        pkg_names = self._outfile_pkg_names
        if pkg_names is None:
            pkg_names = self._outfile_pkg_names = set()
            try:
                with open(self.outfile, 'rt') as fp:
                    pkg_names.update(l.split('==')[0].lower() for l in fp)
            except IOError:
                pass  # Act as if file is empty

        return pkg.lower() in pkg_names

    @property
    def pin_command(self):
        """Compose pip-compile shell command"""
        parts = [
            'pip-compile',
            '--no-header',
            '--verbose',
            '--rebuild',
            '--no-index',
        ]
        if OPTIONS['upgrade_packages']:
            parts.extend(
                '--upgrade-package=' + p for p in OPTIONS['upgrade_packages']
                if self.is_package_in_outfile(p))

        if OPTIONS['upgrade']:
            parts.append('--upgrade')
        if self.add_hashes:
            parts.append('--generate-hashes')

        parts.extend(['--output-file', self.outfile, self.infile])
        return parts

    def fix_lockfile(self):
        """Run each line of outfile through fix_pin"""
        with open(self.outfile, 'rt') as fp:
            lines = [
                self.fix_pin(line)
                for line in self.concatenated(fp)
            ]
        with open(self.outfile, 'wt') as fp:
            fp.writelines([
                line + '\n'
                for line in lines
                if line is not None
            ])

    @staticmethod
    def concatenated(fp):
        """Read lines from fp concatenating on backslash (\\)"""
        line_parts = []
        for line in fp:
            line = line.strip()
            if line.endswith('\\'):
                line_parts.append(line[:-1].rstrip())
            else:
                line_parts.append(line)
                yield ' '.join(line_parts)
                line_parts[:] = []
        if line_parts:
            # Impossible:
            raise RuntimeError("Compiled file ends with backslash \\")

    def fix_pin(self, line):
        """
        Fix dependency by removing post-releases from versions
        and loosing constraints on internal packages.
        Drop packages from ignore set

        Also populate packages set
        """
        dep = Dependency(line)
        if dep.valid:
            if dep.package in self.ignore:
                ignored_version = self.ignore[dep.package]
                if ignored_version is not None:
                    # ignored_version can be None to disable conflict detection
                    if dep.version and dep.version != ignored_version:
                        logger.error(
                            "Package %s was resolved to different "
                            "versions in different environments: %s and %s",
                            dep.package, dep.version, ignored_version,
                        )
                        raise RuntimeError(
                            "Please add constraints for the package "
                            "version listed above"
                        )
                return None
            self.packages[dep.package] = dep.version
            if self.forbid_post or dep.is_compatible:
                # Always drop post for internal packages
                dep.drop_post()
            return dep.serialize()
        return line.strip()

    def add_references(self, other_names):
        """Add references to other_names in outfile"""
        if not other_names:
            # Skip on empty list
            return
        with open(self.outfile, 'rt') as fp:
            header, body = self.split_header(fp)
        with open(self.outfile, 'wt') as fp:
            fp.writelines(header)
            fp.writelines(
                '-r {0}.{1}\n'.format(other_name, OPTIONS['out_ext'])
                for other_name in sorted(other_names)
            )
            fp.writelines(body)

    @staticmethod
    def split_header(fp):
        """
        Read file pointer and return pair of lines lists:
        first - header, second - the rest.
        """
        body_start, header_ended = 0, False
        lines = []
        for line in fp:
            if line.startswith('#') and not header_ended:
                # Header text
                body_start += 1
            else:
                header_ended = True
            lines.append(line)
        return lines[:body_start], lines[body_start:]

    def replace_header(self, header_text):
        """Replace pip-compile header with custom text"""
        with open(self.outfile, 'rt') as fp:
            _, body = self.split_header(fp)
        with open(self.outfile, 'wt') as fp:
            fp.write(header_text)
            fp.writelines(body)
