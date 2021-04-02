"""
Disable upgrades
================

When new dependencies are added it's tempting to keep everything else the same.
To recompile ``.txt`` keeping satisfying version use ``--no-upgrade``:

.. code-block:: text

    --upgrade / --no-upgrade    Upgrade package version (default true)

The option has no effect if there are no existing ``.txt`` files.

Upgrade only selected packages
==============================

To upgrade only one package and keep everything else untouched,
use following option:

.. code-block:: text

    -P, --upgrade-package TEXT  Only upgrade named package.
                                Can be supplied multiple times.

Under the hood it uses `the same option of pip-compile`_
and runs compilation only for files that have one of the passed packages.

This option implies ``--no-upgrade`` and takes precedence over ``--upgrade``.

Thanks to `Jonathan Rogers <https://github.com/JonathanRRogers>`_.

.. _`the same option of pip-compile`: \
        https://github.com/jazzband/pip-tools#updating-requirements
"""

from .base import BaseFeature, ClickOption
from .forward import ForwardOption


class UpgradeAll(ForwardOption):
    """Upgrade all packages in all environments."""

    OPTION_NAME = 'upgrade'
    CLICK_OPTION = ClickOption(
        long_option='--upgrade/--no-upgrade',
        default=True,
        is_flag=True,
        help_text='Upgrade package version (default true)',
    )
    enabled_pin_options = ['--upgrade']

    def __init__(self, controller):
        self._controller = controller

    @property
    def enabled(self):
        """Whether global upgrade is enabled."""
        return self.value and not self._controller.upgrade_selected.active


class UpgradeSelected(BaseFeature):
    """Upgrade only specific packages in all environments."""

    OPTION_NAME = 'upgrade_packages'
    CLICK_OPTION = ClickOption(
        long_option='--upgrade-package',
        short_option='-P',
        multiple=True,
        help_text='Only upgrade named package. '
                  'Can be supplied multiple times.',
    )

    def __init__(self, controller):
        self._controller = controller
        self.reset()

    def reset(self):
        """Clear cached packages."""
        self._env_packages_cache = {}

    @property
    def package_names(self):
        """List of package names to upgrade."""
        return self.value or []

    @property
    def active(self):
        """Whether selective upgrade is active."""
        return bool(self.package_names)

    def pin_options(self):
        """Pin command options for upgrading specific packages."""
        return [
            '--upgrade-package=' + package
            for package in self.package_names
        ]

    def has_package(self, in_path, package_name):
        """Whether specified package name is already in the outfile."""
        return package_name.lower() in self._get_packages(in_path)

    def _get_packages(self, in_path):
        if in_path not in self._env_packages_cache:
            self._env_packages_cache[in_path] = self._read_packages(
                self._compose_output_file_path(in_path)
            )
        return self._env_packages_cache[in_path]

    @staticmethod
    def _read_packages(outfile):
        try:
            with open(outfile) as fp:
                return set(
                    line.split('==', 1)[0].lower()
                    for line in fp
                    if '==' in line
                )
        except IOError:
            # Act as if file is empty
            return set()

    def _compose_output_file_path(self, in_path):
        return self._controller.compose_output_file_path(in_path)

    def affected(self, in_path):
        """Whether environment was affected by upgraded packages."""
        if not self.active:
            return True
        return any(
            self.has_package(in_path, package_name)
            for package_name in self.package_names
        )
