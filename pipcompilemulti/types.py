"""Shared data shapes used by discovery and configuration."""

from collections.abc import Collection
from typing import TypeAlias, TypedDict

OptionValue: TypeAlias = str | bool | list[str] | tuple[str, ...] | None
ConfigSection: TypeAlias = tuple[str, dict[str, OptionValue]]


class PipeArguments(TypedDict, total=False):
    """Optional stdout/stderr redirection for the compiler subprocess."""

    stdout: int
    stderr: int


class EnvironmentPaths(TypedDict):
    """Paths required by dependency graph operations."""

    in_path: str
    refs: Collection[str]


class EnvironmentSpec(EnvironmentPaths, total=False):
    """Discovered environment; graph-only callers may omit its display name."""

    name: str
