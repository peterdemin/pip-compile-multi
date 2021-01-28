"""
Skip constraints in comments of output files
============================================

When input files contain constraint references (e.g. '-c constraints.in'),
pip-compile adds it to "via" comments. For example::

    rsa==3.4.2
         # via
         #   -c constraints.txt
         #   google-auth

When this option is enabled that snippet will be converted to::

    rsa==3.4.2
         # via google-auth

Saving two lines in .txt file.

.. code-block:: text

    --skip-constraints      Remove constraints from "via" comments.

This feature is especially useful in combination with :ref:`autoresolve`.
"""

import re

from .base import BaseFeature, ClickOption


class SkipConstraintComments(BaseFeature):
    """Remove lines like ``-c file.txt`` from comments in output files."""

    OPTION_NAME = 'skip_constraints'
    CLICK_OPTION = ClickOption(
        long_option='--skip-constraints',
        is_flag=True,
        default=False,
        help_text='Remove constraints from "via" comments.',
    )
    _RE_VIA_COMMENT = re.compile(
        r'^\s*# via$'
    )
    _RE_CONSTRAINT_COMMENT = re.compile(
        r'^\s*#\s+-c \S+$'
    )
    _RE_PACKAGE_COMMENT = re.compile(
        r'^\s*#\s+((?:-r )?\S+)$'
    )

    @property
    def enabled(self):
        """Whether feature was explicitly enabled or not."""
        return self.value

    def process_dependency_comments(self, comment):
        """Remove constraint comments if feature is enabled."""
        if self.enabled:
            return self._drop_sink_comment(comment)
        return comment

    def _drop_sink_comment(self, comment):
        r"""Erase sink constraint from comments.

        >>> feature = SkipConstraintComments()
        >>> feature._drop_sink_comment("\n# via\n#   -c smth\n#   pkg\n")
        '\n# via pkg'
        >>> feature._drop_sink_comment("  # via pkg")
        '  # via pkg'
        """
        lines = comment.splitlines()
        if len(lines) > 2 and self._RE_VIA_COMMENT.match(lines[1]):
            result = lines[:2]
            for line in lines[2:]:
                if self._RE_CONSTRAINT_COMMENT.match(line):
                    continue
                result.append(line)
            return "\n".join(self._collapse_single_via(result))
        return comment

    def _collapse_single_via(self, lines):
        r"""Combine via into a single line when it has only two lines.

        >>> feature = SkipConstraintComments()
        >>> feature._collapse_single_via(["", "# via", "#   pkg"])
        ['', '# via pkg']
        >>> feature._collapse_single_via(["  # via pkg"])
        ['  # via pkg']
        >>> feature._collapse_single_via(["", "# via", "#   -r file"])
        ['', '# via -r file']
        """
        if len(lines) == 3:
            matchobj = self._RE_PACKAGE_COMMENT.match(lines[2])
            if matchobj:
                package = matchobj.group(1)
                return [lines[0], lines[1] + ' ' + package]
        return lines
