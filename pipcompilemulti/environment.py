"""Environment class"""

import os
import re
import logging

from .options import OPTIONS
from .locker import Locker, PipCompile
from .dependency import dependency_builder_factory


logger = logging.getLogger("pip-compile-multi")


def environment_factory(name,
                        ignore=None,
                        forbid_post=False,
                        add_hashes=False):
    """Create Environment instance"""
    infile = os.path.join(
        OPTIONS.discovery.directory,
        '{0}.{1}'.format(name, OPTIONS.discovery.in_ext),
    )
    outfile = os.path.join(
        OPTIONS.discovery.directory,
        '{0}.{1}'.format(name, OPTIONS.discovery.out_ext),
    )
    return Environment(
        name,
        infile,
        outfile,
        OPTIONS.discovery.out_ext,
        locker=Locker(
            outfile=outfile,
            forbid_post=forbid_post,
            ignore=ignore,
            dependency_builder=dependency_builder_factory(
                compatible=OPTIONS.fix.compatible,
                upgrade=OPTIONS.compile.upgrade,
            ),
            compiler=PipCompile(
                infile=infile,
                outfile=outfile,
                upgrade=OPTIONS.compile.upgrade,
                generate_hashes=add_hashes,
            ),
        )
    )


class Environment(object):
    """requirements file"""

    RE_REF = re.compile(r'^(?:-r|--requirement)\s*(?P<path>\S+).*$')

    def __init__(self, name, infile, outfile, out_ext, locker):
        """
        name - name of the environment, e.g. base, test
        ignore - set of package names to omit in output
        """
        self.name = name
        self.infile = infile
        self.outfile = outfile
        self.out_ext = out_ext
        self.locker = locker
        self.packages = {}

    def create_lockfile(self):
        """
        Write recursive dependencies list to outfile
        with hard-pinned versions.
        Then fix it.
        """
        self.packages.update(self.locker.create_lockfile())

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
                '-r {0}.{1}\n'.format(other_name, self.out_ext)
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
