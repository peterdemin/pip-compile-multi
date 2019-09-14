"""
Requirements Files Extensions
=============================

By default ``pip-compile-multi`` compiles ``*.txt`` from ``*.in`` files.
While this is a common naming pattern, each project can use it's own:

.. code-block:: text

    -i, --in-ext TEXT      File extension of input files
    -o, --out-ext TEXT     File extension of output files
"""

from .base import BaseFeature, ClickOption


class InputExtension(BaseFeature):
    """Override input file extension."""

    OPTION_NAME = 'in_ext'
    CLICK_OPTION = ClickOption(
        long_option='--in-ext',
        short_option='-i',
        default="in",
        is_flag=False,
        help_text='File extension of input files.',
    )

    def compose_input_file_name(self, env_name):
        """Compose file name given environment name.

        >>> InputExtension().compose_input_file_name('base')
        'base.in'
        """
        return '{0}.{1}'.format(env_name, self.value)


class OutputExtension(BaseFeature):
    """Override output file extension."""

    OPTION_NAME = 'out_ext'
    CLICK_OPTION = ClickOption(
        long_option='--out-ext',
        short_option='-o',
        default="txt",
        is_flag=False,
        help_text='File extension of output files.',
    )

    def compose_output_file_name(self, env_name):
        """Compose file name given environment name.

        >>> OutputExtension().compose_output_file_name('base')
        'base.txt'
        """
        return '{0}.{1}'.format(env_name, self.value)
