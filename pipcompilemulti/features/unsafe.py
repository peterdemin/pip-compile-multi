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
generating requirements files which `cannot be installed`_.

.. _cannot be installed: https://github.com/jazzband/pip-tools/issues/806
"""

from .base import ClickOption
from .forward import ForwardOption


class AllowUnsafe(ForwardOption):
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
    enabled_pin_options = ['--allow-unsafe']
