"""
Allow Unsafe Packages
=====================

If your project depends on packages that include ``setuptools``
or other packages considered "unsafe" by ``pip-tools`` and you
still wish to have them included in the resulting requirements files,
you can pass this option to do so:

.. code-block:: text

    -s, --allow-unsafe          Whether or not to include 'unsafe' packages
                                in generated requirements files. Consult
                                pip-compile --help for more information

This is commonly used with --generate-hashes to avoid
generating requirements files which cannot be installed.
"""

from .base import BaseFeature, ClickOption


class AllowUnsafe(BaseFeature):
    """Use pip-tools cache, or rebuild from scratch."""

    OPTION_NAME = 'allow_unsafe'
    CLICK_OPTION = ClickOption(
        long_option='--allow-unsafe',
        short_option='-s',
        is_flag=True,
        default=False,
        help_text="Whether or not to include 'unsafe' packages "
                  'in generated requirements files. '
                  'Consult pip-compile --help for more information'
    )

    @property
    def enabled(self):
        """Are unsafe packages allowed."""
        return self.value

    def pin_options(self):
        """Return command-line options for pin command.

        >>> from pipcompilemulti.options import OPTIONS
        >>> unsafe = AllowUnsafe()
        >>> unsafe.pin_options()
        []
        >>> OPTIONS['allow_unsafe'] = True
        >>> unsafe.pin_options()
        ['--allow-unsafe']
        """
        if self.enabled:
            return ['--allow-unsafe']
        return []
