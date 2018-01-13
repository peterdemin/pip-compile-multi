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
import glob
import logging
import itertools
import subprocess
from fnmatch import fnmatch

import click
from toposort import toposort_flatten


__author__ = 'Peter Demin'
__email__ = 'peterdemin@gmail.com'
__version__ = '1.1.0'


ENVIRONMENTS = [
    {'name': 'base', 'ref': None, 'allow_post': False},
    {'name': 'test', 'ref': 'base', 'allow_post': True},
    {'name': 'local', 'ref': 'test', 'allow_post': True},
]
logger = logging.getLogger("pip-compile-multi")


OPTIONS = {
    'compatible_patterns': [],
    'base_dir': 'requirements',
    'allow_post': ['test', 'local'],
    'in_ext': 'in',
    'out_ext': 'txt',
}


@click.command()
@click.option('--compatible', '-c', multiple=True,
              help='Glob expression for packages with compatible (~=) '
                   'version constraint')
@click.option('--post', '-p', multiple=True,
              help='Environment name (base, test, etc) that can have '
                   'packages with post-release versions (1.2.3.post777)')
@click.option('--directory', '-d', default=OPTIONS['base_dir'],
              help='Directory path with requirements files')
@click.option('--in-ext', '-i', default=OPTIONS['in_ext'],
              help='File extension of input files')
@click.option('--out-ext', '-o', default=OPTIONS['out_ext'],
              help='File extension of output files')
def entry(compatible, post, directory, in_ext, out_ext):
    """Click entry point"""
    OPTIONS.update({
        'compatible_patterns': compatible,
        'allow_post': set(post),
        'base_dir': directory,
        'in_ext': in_ext,
        'out_ext': out_ext,
    })
    main()


def main():
    """
    Compile requirements files for all environments.
    """
    logging.basicConfig(level=logging.DEBUG)
    pinned_packages = {}
    env_confs = discover(
        os.path.join(
            OPTIONS['base_dir'],
            '*.' + OPTIONS['in_ext'],
        )
    )
    for conf in env_confs:
        ignored_sets = [
            pinned_packages[name]
            for name in conf['refs']
        ]
        rrefs = recursive_refs(env_confs, conf['name'])
        env = Environment(
            name=conf['name'],
            ignore=merged_packages(pinned_packages, rrefs),
            allow_post=conf['name'] in OPTIONS['allow_post'],
        )
        logger.info("Locking %s to %s. References: %r",
                    env.infile, env.outfile, sorted(rrefs))
        env.create_lockfile()
        for ref in conf['refs']:
            env.reference(ref)
        pinned_packages[conf['name']] = set(env.packages)


def merged_packages(env_packages, names):
    """
    Return union set of environment packages with given names

    >>> sorted(merged_packages(
    ...     {
    ...         'a': {1, 2},
    ...         'b': {2, 3},
    ...         'c': {3, 4}
    ...     },
    ...     ['a', 'b']
    ... ))
    [1, 2, 3]
    """
    ignored_sets = [
        env_packages[name]
        for name in names
    ]
    if ignored_sets:
        return set.union(*ignored_sets)
    return set()


def recursive_refs(envs, name):
    """
    Return set of recursive refs for given env name

    >>> sorted(recursive_refs([
    ...     {'name': 'base', 'refs': []},
    ...     {'name': 'test', 'refs': ['base']},
    ...     {'name': 'local', 'refs': ['test']},
    ... ], 'local'))
    ['base', 'test']
    """
    refs_by_name = {
        env['name']: set(env['refs'])
        for env in envs
    }
    refs = refs_by_name[name]
    if refs:
        indirect_refs = set(itertools.chain.from_iterable([
            recursive_refs(envs, ref)
            for ref in refs
        ]))
    else:
        indirect_refs = set()
    return set.union(refs, indirect_refs)


class Environment(object):
    """requirements file"""

    IN_EXT = '.in'
    OUT_EXT = '.txt'
    RE_REF = re.compile('^(?:-r|--requirement)\s*(?P<path>\S+).*$')

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
        for pattern in OPTIONS['compatible_patterns']:
            if fnmatch(self.package.lower(), pattern):
                return True
        return False

    def drop_post(self):
        post_index = self.version.find('.post')
        if post_index >= 0:
            self.version = self.version[:post_index]


def discover(glob_pattern):
    """
    Find all files matching given glob_pattern,
    parse them, and return list of environments:

    >>> envs = discover("requirements/*.in")
    >>> envs == [
    ...     {'name': 'base', 'refs': []},
    ...     {'name': 'test', 'refs': ['base']},
    ...     {'name': 'local', 'refs': ['test']},
    ... ]
    True
    """
    in_paths = glob.glob(glob_pattern)
    names = {
        extract_env_name(path): path
        for path in in_paths
    }
    return order_by_refs([
        {'name': name, 'refs': Environment.parse_references(in_path)}
        for name, in_path in names.items()
    ])


def extract_env_name(file_path):
    """Return environment name for given requirements file path"""
    return os.path.splitext(os.path.basename(file_path))[0]


def order_by_refs(envs):
    """
    Return topologicaly sorted list of environments.
    I.e. all referenced environments are placed before their references.
    """
    topology = {
        env['name']: set(env['refs'])
        for env in envs
    }
    by_name = {
        env['name']: env
        for env in envs
    }
    return [
        by_name[name]
        for name in toposort_flatten(topology)
    ]


if __name__ == '__main__':
    main()
