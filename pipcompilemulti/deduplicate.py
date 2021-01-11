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
        return merged_packages(self.env_packages, rrefs)

    def recursive_refs(self, in_path):
        """Return recursive list of environment names referenced by in_path."""
        if self.env_confs is None:
            return {}
        return recursive_refs(self.env_confs, in_path)
