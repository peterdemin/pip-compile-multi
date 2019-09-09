"""Aggregate all features in a single controller."""

from .use_cache import UseCache
from .file_extensions import InputExtension, OutputExtension
from .base_dir import BaseDir
from .compatible import Compatible
from .forbid_post import ForbidPost
from .add_hashes import AddHashes


class FeaturesController:
    """Gateway to a list of features."""

    def __init__(self):
        self.use_cache = UseCache()
        self.input_extension = InputExtension()
        self.output_extension = OutputExtension()
        self.base_dir = BaseDir()
        self.compatible = Compatible()
        self.forbid_post = ForbidPost()
        self.add_hashes = AddHashes()
        self._features = [
            self.use_cache,
            self.input_extension,
            self.output_extension,
            self.base_dir,
            self.compatible,
            self.forbid_post,
            self.add_hashes,
        ]

    def bind(self, command):
        """Bind all features to click command."""
        for feature in self._features:
            command = feature.bind(command)
        return command

    def pin_options(self, env_name):
        """Return list of options to pin command."""
        options = self.use_cache.pin_options()
        options.extend(self.add_hashes.pin_options(env_name))
        return options

    def compose_input_file_path(self, env_name):
        """Return input file path by environment name."""
        return self.base_dir.file_path(
            self.input_extension.compose_input_file_name(env_name)
        )

    def compose_output_file_path(self, env_name):
        """Return output file path by environment name."""
        return self.base_dir.file_path(
            self.output_extension.compose_output_file_name(env_name)
        )

    def compose_output_file_name(self, env_name):
        """Return output file name by environment name."""
        return self.output_extension.compose_output_file_name(env_name)

    def drop_post(self, env_name, package_name, version):
        """Whether post versions are forbidden for passed environment name."""
        if self.forbid_post.post_forbidden(env_name):
            return self.forbid_post.drop_post(version)
        if self.compatible.is_matched(package_name):
            return self.forbid_post.drop_post(version)
        return version

    def constraint(self, package_name):
        """Return ``~=`` if package_name matches patterns, ``==`` otherwise."""
        return self.compatible.constraint(package_name)

    def on_discover(self, env_confs):
        """Configure features with a list of discovered environments."""
        self.add_hashes.on_discover(env_confs)