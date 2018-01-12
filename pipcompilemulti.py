#!/usr/bin/env python
"""
Build locked requirements files for each of:
    base.in
    test.in
    local.in

External dependencies are hard-pinned using ==
Internal dependencies are soft-pinned using ~=
".post23423" version postfixes are truncated
"""

import os
import re
import subprocess
import logging
from fnmatch import fnmatch

import click


__author__ = 'Peter Demin'
__email__ = 'peterdemin@gmail.com'
__version__ = '1.0.5'


ENVIRONMENTS = [
    {'name': 'base', 'ref': None, 'allow_post': False},
    {'name': 'test', 'ref': 'base', 'allow_post': True},
    {'name': 'local', 'ref': 'test', 'allow_post': True},
]
logger = logging.getLogger("pip-compile-multi")


config = {
    'compatible_patterns': [],
    'base_dir': 'requirements',
}


@click.command()
@click.option('--compatible', '-c', multiple=True,
              help='Glob expression for packages with compatible (~=) '
                   'version constraint')
def entry(compatible):
    """Click entry point"""
    config['compatible_patterns'] = compatible
    main()


def main():
    """
    Compile requirements files for all environments.
    """
    logging.basicConfig(level=logging.DEBUG)
    pinned_packages = set()
    for conf in ENVIRONMENTS:
        env = Environment(
            name=conf['name'],
            ignore=pinned_packages,
            allow_post=conf['allow_post'],
        )
        env.create_lockfile()
        if conf['ref']:
            env.reference(conf['ref'])
        pinned_packages.update(env.packages)


class Environment(object):
    """requirements file"""

    IN_EXT = '.in'
    OUT_EXT = '.txt'
    RE_REF = re.compile(r'^-r\s+(\S+)$')

    def __init__(self, name, ignore=None, allow_post=False):
        """
        name - name of the environment, e.g. base, test
        ignore - set of package names to omit in output
        """
        self.name = name
        self.ignore = ignore or set()
        self.allow_post = allow_post
        self.packages = set()

    def create_lockfile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        Then fix it.
        """
        logger.info("Locking %s to %s", self.infile, self.outfile)
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

    @classmethod
    def parse_references(cls, filename):
        """
        Read filename line by line searching for pattern:

        -r file.in

        return list of matched file names without extension.
        E.g. ['file']
        """
        references = []
        for line in open(filename):
            matched = cls.RE_REF.match(line)
            if matched:
                reference = matched.group(1)
                reference_base = os.path.splitext(reference)[0]
                references.append(reference_base)
        return references

    @property
    def infile(self):
        return os.path.join('requirements',
                            '{0}{1}'.format(self.name, self.IN_EXT))

    @property
    def outfile(self):
        return os.path.join('requirements',
                            '{0}{1}'.format(self.name, self.OUT_EXT))

    @property
    def pin_command(self):
        return [
            'pip-compile',
            '--rebuild',
            '--upgrade',
            '--no-index',
            '--output-file', self.outfile,
            self.infile,
        ]

    def fix_lockfile(self):
        """
        Run each line of outfile through fix_pin
        """
        with open(self.outfile, 'rt') as fp:
            lines = [
                self.fix_pin(line)
                for line in fp
            ]
        with open(self.outfile, 'wt') as fp:
            fp.writelines([
                line + '\n'
                for line in lines
                if line is not None
            ])

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
                return None
            self.packages.add(dep.package)
            if not self.allow_post or dep.is_compatible:
                # Always drop post for internal packages
                dep.drop_post()
            return dep.serialize()
        return line.strip()

    def reference(self, other_name):
        """
        Add reference to other_name in outfile
        """
        ref = other_name + self.OUT_EXT
        with open(self.outfile, 'rt') as fp:
            content = fp.read()
        with open(self.outfile, 'wt') as fp:
            fp.write('-r {0}\n'.format(ref))
            fp.write(content)


class Dependency(object):
    """Single dependency line"""

    COMMENT_JUSTIFICATION = 26

    # Example:
    # unidecode==0.4.21         # via myapp
    # [package]  [version]      [comment]
    RE_DEPENDENCY = re.compile(
        r'(?iu)(?P<package>[^=]+)'
        r'=='
        r'(?P<version>[^ ]+)'
        r' *'
        r'(?:(?P<comment>#.*))?$'
    )

    def __init__(self, line):
        m = self.RE_DEPENDENCY.match(line)
        if m:
            self.valid = True
            self.package = m.group('package')
            self.version = m.group('version').strip()
            self.comment = (m.group('comment') or '').strip()
        else:
            self.valid = False

    def serialize(self):
        """
        Render dependency back in string using:
            ~= if package is internal
            == otherwise
        """
        equal = '~=' if self.is_compatible else '=='
        package_version = '{package}{equal}{version}'.format(
            package=self.package,
            version=self.version,
            equal=equal,
        )
        return '{0}{1}'.format(
            package_version.ljust(self.COMMENT_JUSTIFICATION),
            ' ' + self.comment if self.comment else '',
        ).rstrip()

    @property
    def is_compatible(self):
        for pattern in config['compatible_patterns']:
            if fnmatch(self.package.lower(), pattern):
                return True
        return False

    def drop_post(self):
        post_index = self.version.find('.post')
        if post_index >= 0:
            self.version = self.version[:post_index]


if __name__ == '__main__':
    main()
