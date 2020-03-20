"""
Requirements Directory
======================

While it's a common practice to put requirements files inside ``requirements``
directory, it's not always the case.
The directory can be overridden with this option:

.. code-block:: text

    -d, --directory TEXT   Directory path with requirements files
"""

import os

from .base import BaseFeature, ClickOption


class BaseDir(BaseFeature):
    """Override input file extension."""

    OPTION_NAME = 'base_dir'
    CLICK_OPTION = ClickOption(
        long_option='--directory',
        short_option='-d',
        default="requirements",
        is_flag=False,
        help_text='Directory path with requirements files.',
    )

    @property
    def path(self):
        """Get the base directory path.

        >>> BaseDir().path == 'requirements'
        True
        """
        return self.value

    def file_path(self, file_name):
        """Compose file path for a given file name.

        >>> import os.path
        >>> expected = os.path.join('requirements', 'base.txt')
        >>> expected == BaseDir().file_path('base.txt')
        True
        """
        return os.path.join(self.value, file_name)
