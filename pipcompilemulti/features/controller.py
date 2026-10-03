"""Aggregate all features in a single controller."""

import os
import sys
from collections.abc import Callable, Collection
from functools import wraps
from typing import Any, TypeVar, cast

from ..types import EnvironmentSpec, OptionValue, PipeArguments
from .add_hashes import AddHashes
from .annotate_index import AnnotateIndex
from .autoresolve import Autoresolve
from .backtracking import Backtracking
from .base import BaseFeature
from .base_dir import BaseDir
from .build_isolation import BuildIsolation
from .compatible import Compatible
from .emit_find_links import EmitFindLinks
from .emit_trusted_host import EmitTrustedHost
from .extra_index_url import ExtraIndexUrl
from .file_extensions import InputExtension, OutputExtension
from .forbid_post import ForbidPost
from .header import CustomHeader
from .limit_in_paths import LimitInPaths
from .live_output import LiveOutput
from .python_target import PythonPlatform, PythonVersion
from .skip_constraint_comments import SkipConstraintComments
from .strip_extras import StripExtras
from .unsafe import AllowUnsafe
from .upgrade import UpgradeAll, UpgradeSelected
from .use_cache import UseCache
from .use_uv import UseUV

Command = TypeVar("Command", bound=Callable[..., Any])


class FeaturesController:
    """Gateway to a list of features."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self) -> None:
        self.add_hashes = AddHashes(self)
        self.allow_unsafe = AllowUnsafe()
        self.annotate_index = AnnotateIndex()
        self.autoresolve = Autoresolve()
        self.backtracking = Backtracking()
        self.base_dir = BaseDir()
        self.build_isolation = BuildIsolation()
        self.compatible = Compatible()
        self.emit_find_links = EmitFindLinks()
        self.emit_trusted_host = EmitTrustedHost()
        self.extra_index_url = ExtraIndexUrl()
        self.forbid_post = ForbidPost()
        self.header = CustomHeader()
        self.input_extension = InputExtension()
        self.limit_in_paths = LimitInPaths()
        self.live_output = LiveOutput()
        self.output_extension = OutputExtension()
        self.python_platform = PythonPlatform()
        self.python_version = PythonVersion()
        self.skip_constraint_comments = SkipConstraintComments()
        self.strip_extras = StripExtras()
        self.upgrade_all = UpgradeAll(self)
        self.upgrade_selected = UpgradeSelected(self)
        self.use_cache = UseCache()
        self.use_uv = UseUV()
        self._features: list[BaseFeature[Any]] = [
            self.add_hashes,
            self.allow_unsafe,
            self.annotate_index,
            self.autoresolve,
            self.backtracking,
            self.base_dir,
            self.build_isolation,
            self.compatible,
            self.emit_find_links,
            self.emit_trusted_host,
            self.extra_index_url,
            self.forbid_post,
            self.header,
            self.input_extension,
            self.limit_in_paths,
            self.live_output,
            self.output_extension,
            self.python_platform,
            self.python_version,
            self.skip_constraint_comments,
            self.strip_extras,
            self.upgrade_all,
            self.upgrade_selected,
            self.use_cache,
            self.use_uv,
        ]

    def bind(self, command: Command) -> Command:
        """Bind all features to click command."""

        @wraps(command)
        def save_command_options(*args: Any, **kwargs: OptionValue) -> Any:
            """Save option values and call original command without it."""
            for feature in self._features:
                feature.extract_option(kwargs)
            return command(*args, **kwargs)

        for feature in self._features:
            save_command_options = feature.bind(save_command_options)
        return cast(Command, save_command_options)

    def pin_command(self) -> list[str]:
        """Return list of pin command parameters."""
        if self.use_uv.value:
            executable = self.use_uv.executable()
            if not executable:
                raise RuntimeError(
                    "uv is not installed. Install it with: pip install uv, or brew install uv"
                )
            return executable + [
                "pip",
                "compile",
                "--no-header",
            ]
        # Use the same interpreter binary
        return [
            sys.executable or "python",
            "-m",
            "piptools",
            "compile",
            "--no-header",
            "--verbose",
        ]

    def pin_options(self, in_path: str) -> list[str]:
        """Return list of options to pin command."""
        options: list[str] = []
        options.extend(self.add_hashes.pin_options(in_path))
        options.extend(self.annotate_index.pin_options())
        options.extend(self.build_isolation.pin_options())
        options.extend(self.emit_find_links.pin_options())
        options.extend(self.extra_index_url.pin_options())
        options.extend(self.upgrade_all.pin_options())
        options.extend(self.upgrade_selected.pin_options())
        options.extend(self.python_platform.pin_options(self.use_uv.value))
        options.extend(self.python_version.pin_options(self.use_uv.value))
        if not self.use_uv.value:
            options.extend(self.allow_unsafe.pin_options())
            options.extend(self.emit_trusted_host.pin_options())
            options.extend(self.backtracking.pin_options())
            options.extend(self.use_cache.pin_options())
        options.extend(self.strip_extras.pin_options())
        return options

    def compose_input_file_path(self, basename: str) -> str:
        """Return input file path by environment name."""
        return self.base_dir.file_path(self.input_extension.compose_input_file_name(basename))

    def compose_output_file_path(self, in_path: str) -> str:
        """Return output file path by environment name."""
        return self.output_extension.compose_output_file_path(in_path)

    def drop_post(self, in_path: str, package_name: str, version: str) -> str:
        """Whether post versions are forbidden for passed environment name."""
        if self.forbid_post.post_forbidden(in_path):
            return self.forbid_post.drop_post(version)
        if self.compatible.is_matched(package_name):
            return self.forbid_post.drop_post(version)
        return version

    def constraint(self, package_name: str) -> str:
        """Return ``~=`` if package_name matches patterns, ``==`` otherwise."""
        return self.compatible.constraint(package_name)

    def on_discover(self, env_confs: Collection[EnvironmentSpec]) -> list[EnvironmentSpec]:
        """Configure features with a list of discovered environments.

        Returns a new possibly shorter env list.
        """
        self.upgrade_selected.reset()
        self.limit_in_paths.on_discover(env_confs)
        limited_env_confs = [env for env in env_confs if self.included(env["in_path"])]
        self.add_hashes.on_discover(limited_env_confs)
        self.autoresolve.on_discover(limited_env_confs)
        return limited_env_confs

    def affected(self, in_path: str) -> bool:
        """Whether environment is affected by upgrade command."""
        if self.upgrade_all.enabled:
            return True
        if self.upgrade_selected.affected(in_path):
            return True
        return in_path == self.autoresolve.sink_path()

    def included(self, in_path: str) -> bool:
        """Whether in_path is included directly or by reference."""
        return self.limit_in_paths.included(in_path)

    def get_header_text(self) -> str:
        """Text to put in the beginning of each generated file."""
        return self.header.text

    def sink_in_path(self) -> str | None:
        """Return input sink path if it's enabled. Otherwise None"""
        return self.autoresolve.sink_path()

    def sink_out_path(self) -> str | None:
        """Return sink output path if it's enabled and exists. Otherwise None"""
        infile = self.autoresolve.sink_path()
        if not infile:
            return None
        outfile = self.compose_output_file_path(infile)
        if not os.path.exists(outfile):
            return None
        return outfile

    def process_dependency_comments(self, comment: str) -> str:
        """Process comments of locked dependency (e.g. # via xxx)."""
        return self.skip_constraint_comments.process_dependency_comments(comment)

    def pipe_arguments(self) -> PipeArguments:
        """Values for stdout and stderr arguments to subprocess.Popen."""
        return self.live_output.pipe_arguments()
