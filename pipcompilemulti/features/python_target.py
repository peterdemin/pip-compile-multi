"""
Target Python platform and version
==================================

By default, dependencies are resolved for the interpreter running
``pip-compile-multi``. When the lock file is installed elsewhere,
for example compiled on macOS and deployed to Linux,
packages with platform markers resolve differently
and the lock file may not install at all.

UV can resolve for another platform and Python version instead:

.. code-block:: text

    --python-platform TEXT      Platform to resolve dependencies for,
                                e.g. x86_64-manylinux_2_28. Requires --uv.
    --python-version TEXT       Python version to resolve dependencies for,
                                e.g. 3.12. Requires --uv.

In configuration file, use ``python_platform`` and ``python_version`` options::

    [requirements]
    uv = True
    python_platform = x86_64-manylinux_2_28
    python_version = 3.12

.. note::

    pip-tools has no equivalent, so these options fail without ``--uv``
    rather than silently locking for the current platform.
"""

from .base import BaseFeature, ClickOption


class UvTarget(BaseFeature[str | None]):
    """Forward a resolution target option to uv."""

    _OPTION = ""

    def pin_options(self, use_uv: bool) -> list[str]:
        """Pin command options."""
        if not self.value:
            return []
        if not use_uv:
            raise RuntimeError(f"{self._OPTION} requires --uv")
        return [self._OPTION, self.value]


class PythonPlatform(UvTarget):
    """Resolve dependencies for another platform."""

    _OPTION = "--python-platform"
    OPTION_NAME = "python_platform"
    CLICK_OPTION = ClickOption(
        long_option=_OPTION,
        help_text=(
            "Platform to resolve dependencies for, e.g. x86_64-manylinux_2_28. Requires --uv."
        ),
    )


class PythonVersion(UvTarget):
    """Resolve dependencies for another Python version."""

    _OPTION = "--python-version"
    OPTION_NAME = "python_version"
    CLICK_OPTION = ClickOption(
        long_option=_OPTION,
        help_text="Python version to resolve dependencies for, e.g. 3.12. Requires --uv.",
    )
