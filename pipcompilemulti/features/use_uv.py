"""
Enable UV
=========

UV is an extremely fast Python package installer and resolver written in Rust.
When enabled, pip-compile-multi will use uv's dependency resolver instead of pip-tools.

.. code-block:: text

    --uv / --no-uv      Use uv for dependency resolution.

In configuration file, use ``uv`` option::

    [requirements]
    uv = True

Key differences between uv and pip-tools output:

1. UV is significantly faster at dependency resolution.
   Particularly noticeable in large projects with complex dependency trees.
2. UV's resolver is more aggressive at finding newer versions.

To use UV:

- Install ``uv`` (``pip install uv``)
- Pass ``--uv`` flag to ``pip-compile-multi`` or add ``uv = True`` when using ``requirements`` command.
"""
try:
    import uv  #
    del uv
    UV_AVAILABLE = True
except ImportError:
    UV_AVAILABLE = False

from .base import BaseFeature, ClickOption


class UseUV(BaseFeature):
    """Use uv for dependency resolution.

    This feature enables using uv's fast Rust-based dependency resolver
    instead of pip-tools. UV must be installed (pip install uv>=0.1.0)
    before using this feature.
    """

    OPTION_NAME = 'uv'
    CLICK_OPTION = ClickOption(
        long_option='--uv/--no-uv',
        default=False,
        is_flag=True,
        help_text='Use uv for dependency resolution.',
    )

    @staticmethod
    def is_available():
        """Check if uv package is available"""
        return UV_AVAILABLE
