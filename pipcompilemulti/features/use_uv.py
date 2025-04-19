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

1. Annotations:

   - UV doesn't support pip-tools style annotations (via/from comments).
   - The ``--no-annotate`` flag is automatically added when using uv.

2. Performance:

   - UV is significantly faster at dependency resolution.
   - Particularly noticeable in large projects with complex dependency trees.

3. Output Format:

   - UV produces cleaner output without header comments.
   - Package versions are still pinned exactly like pip-tools.
   - Hash generation (``--generate-hashes``) works the same way.

4. Version Resolution:

   - UV may occasionally resolve to slightly different versions than pip-tools.
   - Both tools respect version constraints equally.
   - UV's resolver is more aggressive at finding newer versions.

To use UV:

- Install ``uv`` (``pip install uv``)
- Use the ``--uv`` flag with commands: ``lock --uv``, ``upgrade --uv``, ``verify --uv``
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
