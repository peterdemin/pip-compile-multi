"""Dependency class"""

import re

from .features import FEATURES


class Dependency(object):
    """Single dependency line"""

    COMMENT_JUSTIFICATION = 26

    # Example:
    # unidecode==0.4.21         # via myapp
    # [package]  [version]      [comment]
    RE_DEPENDENCY = re.compile(
        r'(?iu)(?P<package>\S+)'
        r'=='
        r'(?P<version>\S+)'
        r'\s*'
        r'(?P<hashes>(?:--hash=\S+\s*)+)?'
        r'(?P<comment>#.*)?$'
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
        r'(?P<postfix>\S+)'
        r'\s*'
        r'(?P<comment>#.*)?$'
    )

    def __init__(self, line):
        regular = self.RE_DEPENDENCY.match(line)
        if regular:
            self.valid = True
            self.is_vcs = False
            self.package = regular.group('package')
            self.version = regular.group('version').strip()
            self.hashes = (regular.group('hashes') or '').strip()
            self.comment = (regular.group('comment') or '').strip()
            return
        vcs = self.RE_VCS_DEPENDENCY.match(line)
        if vcs:
            self.valid = True
            self.is_vcs = True
            self.package = vcs.group('package')
            self.version = ''
            self.hashes = ''  # No way!
            self.comment = (vcs.group('comment') or '').strip()
            self.line = line
            return
        self.valid = False

    def serialize(self):
        """
        Render dependency back in string using:
            ~= if package is internal
            == otherwise
        """
        if self.is_vcs:
            return self.without_editable(self.line).strip()
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
            if self.comment:
                lines.append(self.comment)
            return ' \\\n    '.join(lines)
        else:
            return '{0}{1}'.format(
                package_version.ljust(self.COMMENT_JUSTIFICATION),
                self.comment,
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

    def drop_post(self, env_name):
        """Remove .postXXXX postfix from version if needed."""
        self.version = FEATURES.drop_post(env_name, self.package, self.version)
