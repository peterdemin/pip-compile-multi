"""Dependency class"""

import re

from .features import FEATURES


class Dependency(object):  # pylint: disable=too-many-instance-attributes
    r"""Single dependency.

    Comment may span multiple lines.

    >>> print(Dependency(
    ...   "six==1.0\n "
    ...   "    --hash=abcdef\n"
    ...   "    # via\n"
    ...   "    #   app\n"
    ...   "    #   pkg"
    ... ).serialize())
    six==1.0 \
        --hash=abcdef
        # via
        #   app
        #   pkg
    >>> print(Dependency(
    ...   "six==1.0\n"
    ...   "    # via\n"
    ...   "    #   app\n"
    ...   "    #   pkg"
    ... ).serialize())
    six==1.0
        # via
        #   app
        #   pkg
    >>> # Old-style one-line
    >>> print(Dependency("six==1.0    # via pkg").serialize())
    six==1.0                  # via pkg
    >>> print(Dependency("-e https://site#egg=pkg==1\n   # via lib").serialize())
    https://site#egg=pkg==1
       # via lib
    """

    COMMENT_JUSTIFICATION = 26

    # Example:
    # unidecode==0.4.21         # via myapp
    # [package]  [version]      [comment]
    RE_DEPENDENCY = re.compile(
        r'(?iu)(?P<package>\S+)'
        r'=='
        r'(?P<version>\S+)'
        r'(?P<hashes>(?:\s*--hash=\S+)+)?'
        r'(?P<comment>(?:\s*#.*)+)?$'
    )
    RE_EDITABLE_FLAG = re.compile(
        r'^-e '
    )
    # -e git+https://github.com/ansible/docutils.git@master#egg=docutils
    # -e "git+https://github.com/zulip/python-zulip-api.git@
    #                 0.4.1#egg=zulip==0.4.1_git&subdirectory=zulip"
    RE_VCS_DEPENDENCY = re.compile(
        r'(?iu)(?P<editable>-e)?'
        r'\s*'
        r'(?P<prefix>\S+#egg=)'
        r'(?P<package>[a-z0-9-_.]+)'
        r'(?P<postfix>\S*)'
        r'(?P<comment>(?:\s*#.*)+)?$'
    )
    # docutils @ git+https://github.com/ansible/docutils.git@master
    RE_AT_DEPENDENCY = re.compile(
        r'(?iu)(?P<editable>-e)?'
        r'\s*'
        r'(?P<package>[a-z0-9-_.]+)'
        r' @ '
        r'(?P<url>\S+)'
        r'(?P<comment>(?:\s*#.*)+)?$'
    )

    def __init__(self, line):
        self.is_vcs = False
        self.is_at = False
        self.valid = True
        self.line = line
        vcs = self.RE_VCS_DEPENDENCY.match(line)
        if vcs:
            self.is_vcs = True
            self.package = vcs.group('package')
            self.version = ''
            self.hashes = ''  # No way!
            self.comment = (vcs.group('comment') or '').rstrip()
            self.comment_span = self._adjust_span(vcs.span('comment'), vcs)
            return
        at_url = self.RE_AT_DEPENDENCY.match(line)
        if at_url:
            self.is_at = True
            self.package = at_url.group('package')
            self.version = ''
            self.hashes = ''  # ???
            self.comment = (at_url.group('comment') or '').rstrip()
            self.comment_span = self._adjust_span(at_url.span('comment'), at_url)
            return
        regular = self.RE_DEPENDENCY.match(line)
        if regular:
            self.package = regular.group('package')
            self.version = regular.group('version').strip()
            self.hashes = (regular.group('hashes') or '').strip()
            self.comment = (regular.group('comment') or '').rstrip()
            self.comment_span = self._adjust_span(regular.span('comment'), regular)
            return
        self.valid = False

    def serialize(self):
        """
        Render dependency back in string using:
            ~= if package is internal
            == otherwise
        """
        if self.is_vcs or self.is_at:
            return "{}{}".format(
                self.without_editable(self.line[:self.comment_span[0]]).strip(),
                FEATURES.process_dependency_comments(self.comment),
            )
        equal = FEATURES.constraint(self.package)
        package_version = '{package}{equal}{version}  '.format(
            package=self.without_editable(self.package),
            version=self.version,
            equal=equal,
        )
        if self.hashes:
            hashes = self.hashes.split()
            lines = [package_version.strip()]
            lines.extend(hashes)
            result = ' \\\n    '.join(lines)
            result += FEATURES.process_dependency_comments(self.comment)
            return result
        else:
            if self.comment.startswith('\n'):
                return (
                    package_version.rstrip() +
                    FEATURES.process_dependency_comments(self.comment).rstrip()
                )
            return '{0}{1}'.format(
                package_version.ljust(self.COMMENT_JUSTIFICATION),
                self.comment.lstrip(),
            ).rstrip()  # rstrip for empty comment

    @classmethod
    def without_editable(cls, line):
        """
        Remove the editable flag.
        It's there because pip-compile can't yet do without it
        (see https://github.com/jazzband/pip-tools/issues/272 upstream),
        but in the output of pip-compile it's no longer needed.
        """
        if 'git+git@' in line:
            # git+git can't be installed without -e:
            return line
        return cls.RE_EDITABLE_FLAG.sub('', line)

    def drop_post(self, in_path):
        """Remove .postXXXX postfix from version if needed."""
        self.version = FEATURES.drop_post(in_path, self.package, self.version)

    @staticmethod
    def _adjust_span(span, matchobj):
        if span == (-1, -1):
            length = matchobj.span()[1]
            return (length, length)
        return span
