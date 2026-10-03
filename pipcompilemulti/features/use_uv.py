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

- Install ``uv``: ``pip install uv`` next to ``pip-compile-multi``,
  or system-wide, e.g. ``brew install uv``.
  The ``uv`` package installed next to ``pip-compile-multi`` takes precedence
  over the ``uv`` executable found on ``PATH``.
- Pass ``--uv`` flag to ``pip-compile-multi``
  or add ``uv = True`` when using ``requirements`` command.
"""

import importlib.util
import shutil
import sys

from .base import BaseFeature, ClickOption


class UseUV(BaseFeature[bool]):
    """Use uv for dependency resolution.

    This feature enables using uv's fast Rust-based dependency resolver
    instead of pip-tools. UV must be installed, either as a Python package
    or as an executable on PATH, before using this feature.
    """

    OPTION_NAME = "uv"
    CLICK_OPTION = ClickOption(
        long_option="--uv/--no-uv",
        default=False,
        is_flag=True,
        help_text="Use uv for dependency resolution.",
    )

    @staticmethod
    def executable() -> list[str] | None:
        """Command that runs uv, or None when it is not installed."""
        if importlib.util.find_spec("uv"):
            return [sys.executable or "python", "-m", "uv"]
        path = shutil.which("uv")
        return [path] if path else None
