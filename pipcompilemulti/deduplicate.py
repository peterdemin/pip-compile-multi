"""Remove packages included in referenced environments."""

import logging

from pipcompilemulti.utils import recursive_refs, merged_packages


logger = logging.getLogger("pip-compile-multi")


class PackageDeduplicator:
    """Remove packages included in referenced environments."""

    def __init__(self):
        self.env_packages = {}
        self.env_confs = None

    def on_discover(self, env_confs):
        """Save environment references."""
        self.env_confs = env_confs

    def register_packages_for_env(self, in_path, packages):
        """Save environment packages."""
        self.env_packages[in_path] = packages

    def ignored_packages(self, in_path):
        """Get package mapping from name to version for referenced environments."""
        if self.env_confs is None:
            return {}
        rrefs = recursive_refs(self.env_confs, in_path)
        return IgnoredPackages(merged_packages(self.env_packages, rrefs))

    def recursive_refs(self, in_path):
        """Return recursive list of environment names referenced by in_path."""
        if self.env_confs is None:
            return {}
        return recursive_refs(self.env_confs, in_path)


class IgnoredPackages:
    """Mapping from package name to version.

    Handles name normalization for packages like:
    zope.interface, zope-interface, zope_interface.
    """
    _DELIMITERS = ('_', '-', '.')

    def __init__(self, package_versions):
        self._package_versions = package_versions
        self._stems = {
            self._make_stem(name): name
            for name in self._package_versions
        }

    def __getitem__(self, key):
        canonical_key = self._stems[self._make_stem(key)]
        return self._package_versions[canonical_key]

    def __contains__(self, key):
        return self._make_stem(key) in self._stems

    @classmethod
    def _make_stem(cls, name):
        for delim in cls._DELIMITERS:
            name = name.replace(delim, '-')
        return name.lower()
