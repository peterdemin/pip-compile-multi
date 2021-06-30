"""Environment class"""

import os
import re
import sys
import logging
import subprocess

from .dependency import Dependency
from .features import FEATURES
from .deduplicate import PackageDeduplicator
from .utils import extract_env_name


logger = logging.getLogger("pip-compile-multi")


class Environment(object):
    """requirements file"""

    RE_REF = re.compile(r'^(?:-r|--requirement)\s*(?P<path>\S+).*$')
    RE_COMMENT = re.compile(r'^\s*#.*$')

    def __init__(self, in_path, deduplicator=None):
        """
        Args:
            in_path: relative path to input file, e.g. requirements/base.in
        """
        self.in_path = in_path
        self._dedup = deduplicator or PackageDeduplicator()
        self.ignore = self._dedup.ignored_packages(in_path)
        self.packages = {}
        self._outfile_pkg_names = None

    def maybe_create_lockfile(self):
        """
        Write recursive dependencies list to outfile unless the goal is
        to upgrade specific package(s) which don't already appear.
        Populate package ignore set in either case and return
        boolean indicating whether outfile was written.
        """
        logger.info(
            "Locking %s to %s. References: %r",
            self.infile,
            self.outfile,
            sorted(self._dedup.recursive_refs(self.in_path)),
        )
        if not FEATURES.affected(self.in_path):
            self.fix_lockfile()  # populate ignore set
            return False
        self.create_lockfile()
        return True

    def create_lockfile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        Then fix it.
        """
        original_in_file = ""
        sink_out_path = FEATURES.sink_out_path()
        try:
            if sink_out_path and sink_out_path != self.outfile:
                original_in_file = self._read_infile()
                self._inject_sink()
            with subprocess.Popen(self.pin_command, **FEATURES.pipe_arguments()) as process:
                stdout, stderr = process.communicate()
        finally:
            if original_in_file:
                self._restore_in_file(original_in_file)
        if process.returncode == 0:
            self.fix_lockfile()
        else:
            logger.critical("ERROR executing %s", ' '.join(self.pin_command))
            logger.critical("Exit code: %s", process.returncode)
            if stdout:
                logger.critical(stdout.decode('utf-8'))
            if stderr:
                logger.critical(stderr.decode('utf-8'))
            raise RuntimeError("Failed to pip-compile {0}".format(self.infile))

    @classmethod
    def parse_references(cls, filename):
        """
        Read filename line by line searching for pattern:

        -r file.in
        or
        --requirement file.in

        return set of matched file names.
        E.g. {'file1.in', 'file2.in'}
        """
        references = set()
        with open(filename) as fobj:
            for line in fobj:
                matched = cls.RE_REF.match(line)
                if matched:
                    references.add(matched.group('path'))
        return references

    @property
    def name(self):
        """Generate environment name from in_path."""
        return extract_env_name(self.in_path)

    @property
    def infile(self):
        """Path of the input file"""
        return self.in_path

    @property
    def outfile(self):
        """Path of the output file"""
        return FEATURES.compose_output_file_path(self.in_path)

    @property
    def pin_command(self):
        """Compose pip-compile shell command"""
        # Use the same interpreter binary
        python = sys.executable or 'python'
        parts = [
            python, '-m', 'piptools', 'compile',
            '--no-header',
            '--verbose',
        ]
        parts.extend(FEATURES.pin_options(self.in_path))
        parts.extend(['--output-file', self.outfile, self.infile])
        return parts

    def fix_lockfile(self):
        """Run each section of outfile through fix_pin"""
        with open(self.outfile, 'rt') as fp:
            sections = [
                self.fix_pin(section)
                for section in self.parse_sections(self.concatenated(fp))
            ]
        with open(self.outfile, 'wt') as fp:
            fp.writelines([
                section + '\n'
                for section in sections
                if section is not None
            ])
        self._dedup.register_packages_for_env(self.in_path, self.packages)

    @staticmethod
    def concatenated(fp):
        r"""Read lines from fp concatenating on backslash (\\)

        >>> env = Environment('')
        >>> list(env.concatenated([
        ...     'pkg', 'pkg  # comment', 'pkg', '# comment', '# one more',
        ...     'foo', '  # via', '', '  # pkg',
        ... ]))
        ['pkg', 'pkg  # comment', 'pkg', '# comment', '# one more', 'foo', '  # via', '', '  # pkg']
        """
        line_parts = []
        for line in fp:
            line = line.rstrip()
            if line.endswith('\\'):
                line_parts.append(line[:-1].rstrip())
            else:
                line_parts.append(line)
                yield ' '.join(line_parts)
                line_parts[:] = []
        if line_parts:
            # Impossible:
            raise RuntimeError("Compiled file ends with backslash \\")

    def parse_sections(self, lines):
        r"""Combine lines with following comments into sections.

        >>> env = Environment('')
        >>> list(env.parse_sections([
        ...     'pkg', 'pkg  # comment', 'pkg', '# comment', '# one more',
        ...     'foo', '  # via', '', '  # pkg',
        ... ]))
        ['pkg', 'pkg  # comment', 'pkg\n# comment\n# one more', 'foo\n  # via', '\n  # pkg']
        """
        section = []
        for line in lines:
            if self.RE_COMMENT.match(line):
                section.append(line)
            else:
                if section:
                    yield '\n'.join(section)
                section = [line]
        if section:
            yield '\n'.join(section)

    def fix_pin(self, section):
        """
        Fix dependency by removing post-releases from versions
        and loosing constraints on internal packages.
        Drop packages from ignore set

        Also populate packages set
        """
        dep = Dependency(section)
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
            dep.drop_post(self.in_path)
            return dep.serialize()
        return section.rstrip()

    def add_references(self, other_in_paths):
        """Add references to other_in_paths in outfile"""
        if not other_in_paths:
            # Skip on empty list
            return
        with open(self.outfile, 'rt') as fp:
            header, body = self.split_header(fp)
        with open(self.outfile, 'wt') as fp:
            fp.writelines(header)
            fp.writelines(
                '-r {0}\n'.format(
                    FEATURES.compose_output_file_path(other_in_path)
                )
                for other_in_path in sorted(other_in_paths)
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

    def _read_infile(self):
        with open(self.infile, "rt") as fp:
            return fp.read()

    def _restore_in_file(self, content):
        with open(self.infile, "wt") as fp:
            return fp.write(content)

    def _inject_sink(self):
        rel_sink_out_path = os.path.normpath(os.path.relpath(
            FEATURES.sink_out_path(),
            os.path.dirname(self.infile),
        ))
        with open(self.infile, "at") as fp:
            return fp.write("\n\n-c {}\n".format(rel_sink_out_path))
