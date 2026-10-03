"""Remove packages included in referenced environments."""

from __future__ import annotations

import logging
from collections.abc import Collection, Mapping

from pipcompilemulti.utils import merged_packages, recursive_refs

from .types import EnvironmentSpec

logger = logging.getLogger("pip-compile-multi")


class PackageDeduplicator:
    """Remove packages included in referenced environments."""

    def __init__(self) -> None:
        self.env_packages: dict[str, Mapping[str, str | None]] = {}
        self.env_confs: Collection[EnvironmentSpec] | None = None

    def on_discover(self, env_confs: Collection[EnvironmentSpec]) -> None:
        """Save environment references."""
        self.env_confs = env_confs

    def register_packages_for_env(self, in_path: str, packages: Mapping[str, str | None]) -> None:
        """Save environment packages."""
        self.env_packages[in_path] = packages

    def ignored_packages(self, in_path: str) -> IgnoredPackages | dict[str, str | None]:
        """Get package mapping from name to version for referenced environments."""
        if self.env_confs is None:
            return {}
        rrefs = recursive_refs(self.env_confs, in_path)
        return IgnoredPackages(merged_packages(self.env_packages, rrefs))

    def recursive_refs(self, in_path: str) -> Collection[str]:
        """Return recursive list of environment names referenced by in_path."""
        if self.env_confs is None:
            return {}
        return recursive_refs(self.env_confs, in_path)


class IgnoredPackages:
    """Mapping from package name to version.

    Handles name normalization for packages like:
    zope.interface, zope-interface, zope_interface.
    """

    _DELIMITERS = ("_", "-", ".")

    def __init__(self, package_versions: Mapping[str, str | None]) -> None:
        self._package_versions = package_versions
        self._stems = {self._make_stem(name): name for name in self._package_versions}

    def __getitem__(self, key: str) -> str | None:
        canonical_key = self._stems[self._make_stem(key)]
        return self._package_versions[canonical_key]

    def __contains__(self, key: str) -> bool:
        return self._make_stem(key) in self._stems

    @classmethod
    def _make_stem(cls, name: str) -> str:
        for delim in cls._DELIMITERS:
            name = name.replace(delim, "-")
        return name.lower()
