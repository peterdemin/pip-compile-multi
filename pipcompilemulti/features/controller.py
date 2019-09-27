"""Aggregate all features in a single controller."""

from functools import wraps

from .add_hashes import AddHashes
from .annotate_index import AnnotateIndex
from .base_dir import BaseDir
from .compatible import Compatible
from .file_extensions import InputExtension, OutputExtension
from .forbid_post import ForbidPost
from .header import CustomHeader
from .limit_envs import LimitEnvs
from .unsafe import AllowUnsafe
from .upgrade import UpgradeAll, UpgradeSelected
from .use_cache import UseCache


class FeaturesController:
    """Gateway to a list of features."""
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.annotate_index = AnnotateIndex()
        self.use_cache = UseCache()
        self.input_extension = InputExtension()
        self.output_extension = OutputExtension()
        self.base_dir = BaseDir()
        self.compatible = Compatible()
        self.forbid_post = ForbidPost()
        self.add_hashes = AddHashes()
        self.upgrade_all = UpgradeAll(self)
        self.upgrade_selected = UpgradeSelected(self)
        self.limit_envs = LimitEnvs()
        self.header = CustomHeader()
        self.allow_unsafe = AllowUnsafe()
        self._features = [
            self.annotate_index,
            self.use_cache,
            self.input_extension,
            self.output_extension,
            self.base_dir,
            self.compatible,
            self.forbid_post,
            self.add_hashes,
            self.upgrade_all,
            self.upgrade_selected,
            self.limit_envs,
            self.header,
            self.allow_unsafe,
        ]

    def bind(self, command):
        """Bind all features to click command."""
        @wraps(command)
        def save_command_options(*args, **kwargs):
            """Save option values and call original command without it."""
            for feature in self._features:
                feature.extract_option(kwargs)
            return command(*args, **kwargs)

        for feature in self._features:
            save_command_options = feature.bind(save_command_options)
        return save_command_options

    def pin_options(self, env_name):
        """Return list of options to pin command."""
        options = []
        options.extend(self.use_cache.pin_options())
        options.extend(self.add_hashes.pin_options(env_name))
        options.extend(self.allow_unsafe.pin_options())
        options.extend(self.upgrade_all.pin_options())
        options.extend(self.upgrade_selected.pin_options(env_name))
        options.extend(self.annotate_index.pin_options())
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
        self.limit_envs.on_discover(env_confs)
        self.upgrade_selected.reset()

    def affected(self, env_name):
        """Whether environment was affected by upgrade command."""
        if self.upgrade_all.enabled:
            return True
        return self.upgrade_selected.affected(env_name)

    def included(self, env_name):
        """Whether environment is included directly or by reference."""
        return self.limit_envs.included(env_name)

    def get_header_text(self):
        """Text to put in the beginning of each generated file."""
        return self.header.text
