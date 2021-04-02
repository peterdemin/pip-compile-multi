"""Aggregate all features in a single controller."""

import os
from functools import wraps

from .add_hashes import AddHashes
from .annotate_index import AnnotateIndex
from .base_dir import BaseDir
from .compatible import Compatible
from .file_extensions import InputExtension, OutputExtension
from .forbid_post import ForbidPost
from .header import CustomHeader
from .limit_envs import LimitEnvs
from .limit_in_paths import LimitInPaths
from .unsafe import AllowUnsafe
from .upgrade import UpgradeAll, UpgradeSelected
from .use_cache import UseCache
from .autoresolve import Autoresolve
from .skip_constraint_comments import SkipConstraintComments


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
        self.add_hashes = AddHashes(self)
        self.upgrade_all = UpgradeAll(self)
        self.upgrade_selected = UpgradeSelected(self)
        self.limit_envs = LimitEnvs(self)
        self.limit_in_paths = LimitInPaths()
        self.header = CustomHeader()
        self.allow_unsafe = AllowUnsafe()
        self.autoresolve = Autoresolve()
        self.skip_constraint_comments = SkipConstraintComments()
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
            self.limit_in_paths,
            self.limit_envs,
            self.header,
            self.allow_unsafe,
            self.autoresolve,
            self.skip_constraint_comments,
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

    def pin_options(self, in_path):
        """Return list of options to pin command."""
        options = []
        options.extend(self.use_cache.pin_options())
        options.extend(self.add_hashes.pin_options(in_path))
        options.extend(self.allow_unsafe.pin_options())
        options.extend(self.upgrade_all.pin_options())
        options.extend(self.upgrade_selected.pin_options())
        options.extend(self.annotate_index.pin_options())
        return options

    def compose_input_file_path(self, basename):
        """Return input file path by environment name."""
        return self.base_dir.file_path(
            self.input_extension.compose_input_file_name(basename)
        )

    def compose_output_file_path(self, in_path):
        """Return output file path by environment name."""
        return self.output_extension.compose_output_file_path(in_path)

    def drop_post(self, in_path, package_name, version):
        """Whether post versions are forbidden for passed environment name."""
        if self.forbid_post.post_forbidden(in_path):
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
        self.limit_in_paths.on_discover(env_confs)
        self.upgrade_selected.reset()
        self.autoresolve.on_discover(env_confs)

    def affected(self, in_path):
        """Whether environment is affected by upgrade command."""
        if self.upgrade_all.enabled:
            return True
        if self.upgrade_selected.affected(in_path):
            return True
        return in_path == self.autoresolve.sink_path()

    def included(self, in_path):
        """Whether in_path is included directly or by reference."""
        return (
            self.limit_envs.included(in_path) and self.limit_in_paths.included(in_path)
        )

    def get_header_text(self):
        """Text to put in the beginning of each generated file."""
        return self.header.text

    def sink_in_path(self):
        """Return input sink path if it's enabled. Otherwise None"""
        return self.autoresolve.sink_path()

    def sink_out_path(self):
        """Return sink output path if it's enabled and exists. Otherwise None"""
        infile = self.autoresolve.sink_path()
        if not infile:
            return None
        outfile = self.compose_output_file_path(infile)
        if not os.path.exists(outfile):
            return None
        return outfile

    def process_dependency_comments(self, comment):
        """Process comments of locked dependency (e.g. # via xxx)."""
        return self.skip_constraint_comments.process_dependency_comments(comment)
