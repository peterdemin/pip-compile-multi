"""Locker calls pip-compile and fixes output file."""
import logging
import subprocess


logger = logging.getLogger("pip-compile-multi")


class PipCompile(object):
    """pip-compile gateway"""

    def __init__(self,
                 infile,
                 outfile,
                 upgrade=False,
                 generate_hashes=False):
        self.infile = infile
        self.outfile = outfile
        self.upgrade = upgrade
        self.generate_hashes = generate_hashes

    def compile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        """
        process = subprocess.Popen(
            self.pin_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logger.critical("ERROR executing %s", ' '.join(self.pin_command))
            logger.critical("Exit code: %s", process.returncode)
            logger.critical(stdout.decode('utf-8'))
            logger.critical(stderr.decode('utf-8'))
            raise RuntimeError("Failed to pip-compile {0}".format(self.infile))

    @property
    def pin_command(self):
        """Compose pip-compile shell command"""
        parts = [
            'pip-compile',
            '--no-header',
            '--verbose',
            '--rebuild',
            '--no-index',
            '--output-file', self.outfile,
            self.infile,
        ]
        if self.upgrade:
            parts.insert(3, '--upgrade')
        if self.generate_hashes:
            parts.insert(1, '--generate-hashes')
        return parts


class Locker(object):
    """Requirements file locker"""

    def __init__(self,
                 outfile,
                 compiler,
                 dependency_builder,
                 forbid_post=False,
                 ignore=None):
        self.outfile = outfile
        self.forbid_post = forbid_post
        self.compiler = compiler
        self.dependency_builder = dependency_builder
        self.ignore = ignore or {}
        self.packages = {}

    def create_lockfile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        Then fix it.
        Return dictionary of locked packages versions.
        """
        self.compiler.compile()
        self.fix_lockfile()
        return self.packages

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
        """Fix single dependency.

        Remove post-releases from version.
        Loose constraint on internal packages.
        Drop package from ignore set.
        Populate packages set.
        """
        dep = self.dependency_builder(line)
        if dep.valid:
            if dep.package in self.ignore:
                dep.check_version_matches(self.ignore[dep.package])
                return None
            self.packages[dep.package] = dep.version
            if self.forbid_post or dep.is_compatible:
                # Always drop post for internal packages
                dep.drop_post()
            return dep.serialize()
        return line.strip()
