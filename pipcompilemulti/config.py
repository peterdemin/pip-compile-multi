"""Get tasks options from INI file"""

import configparser
import os
import sys
from functools import cache
from typing import cast

from .features.base import BaseFeature, ClickOption
from .types import ConfigSection, OptionValue


def read_config() -> list[ConfigSection] | None:
    """Read requirements.ini and return list of pairs (name, options)
    If no requirements sections found, return None.
    If some sections found, but none matches current runtime, return empty list.
    """
    return filter_sections(read_sections())


def filter_sections(sections: list[ConfigSection]) -> list[ConfigSection] | None:
    """Filter through pairs (name, options)
    leaving only those that match runtime.

    If no requirements sections found, return None.
    If some sections found, but none matches current runtime, return empty list.
    """
    if not sections:
        return None
    jobs: list[ConfigSection] = []
    matchers = python_version_matchers()
    for name, options in sections:
        target_version = options.pop("python", None)
        if target_version in matchers:
            jobs.append((name, options))
    return jobs


def read_sections() -> list[ConfigSection]:
    """Read ini/toml files and return list of pairs (name, options)"""
    sections: list[ConfigSection] = []
    sections.extend(_read_toml_sections())
    sections.extend(_read_cfg_sections())
    return sections


def _read_cfg_sections() -> list[ConfigSection]:
    parser = configparser.ConfigParser()
    parser.read(("requirements.ini", "setup.cfg", "tox.ini"))
    return [
        (name, {key: parse_value(key, parser[name][key]) for key in parser[name]})
        for name in parser.sections()
        if "requirements" in name
    ]


def _read_toml_sections() -> list[ConfigSection]:
    # pylint: disable=import-outside-toplevel
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomli as tomllib
        except ImportError:
            return []

    if not os.path.isfile("pyproject.toml"):
        return []
    with open("pyproject.toml", mode="rb") as fp:
        toml_config = tomllib.load(fp)
    config = toml_config.get("tool", {}).get("requirements")
    if not config:
        return []
    if not all(isinstance(v, dict) for v in config.values()):
        # Allow [tool.requirements] section
        config = {"config": config}
    return [
        (name, {key: parse_value(key, _make_toml_scalar(value)) for key, value in section.items()})
        for name, section in config.items()
    ]


def _make_toml_scalar(v: object) -> str:
    """Coalesce TOML value to string.

    TOML supports richer data types than ini files (strings, arrays,
    floats, ints, etc), however we need to convert all scalar values
    to str for compatibility with the rest of the configuration system,
    which expects strings only.
    """
    return ",".join(cast(list[str], v)) if isinstance(v, list) else str(v)


@cache
def _collect_feature_options() -> dict[str, ClickOption]:
    feature_base: type[BaseFeature[OptionValue]] = BaseFeature
    subclasses = feature_base.__subclasses__()
    for feature_class in feature_base.__subclasses__():
        subclasses.extend(feature_class.__subclasses__())
    return {
        feature_class.OPTION_NAME: feature_class.CLICK_OPTION
        for feature_class in subclasses
        if feature_class.OPTION_NAME and feature_class.CLICK_OPTION
    }


def parse_value(key: str, value: str) -> str | list[str] | bool:
    """Parse value according to the option definition (bool or list)"""
    options = _collect_feature_options()
    click_option = options.get(key)
    if click_option:
        if click_option.multiple:
            return [item.strip() for item in value.split(",")]
        if click_option.is_flag:
            return value.lower() not in ("false", "off", "no")
    return value


def python_version_matchers() -> set[str | None]:
    """Return set of string representations of current python version"""
    version = sys.version_info
    patterns = [
        "{0}",
        "{0}{1}",
        "{0}.{1}",
    ]
    matchers = [pattern.format(*version) for pattern in patterns] + [None]
    return set(matchers)
