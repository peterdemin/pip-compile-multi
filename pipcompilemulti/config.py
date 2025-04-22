"""Get tasks options from INI file"""
import sys
import configparser
from functools import lru_cache

from .features.base import BaseFeature


def read_config():
    """Read requirements.ini and return list of pairs (name, options)
    If no requirements sections found, return None.
    If some sections found, but none matches current runtime, return empty list.
    """
    return filter_sections(read_sections())


def filter_sections(sections):
    """Filter through pairs (name, options)
    leaving only those that match runtime.

    If no requirements sections found, return None.
    If some sections found, but none matches current runtime, return empty list.
    """
    if not sections:
        return None
    jobs = []
    matchers = python_version_matchers()
    for name, options in sections:
        target_version = options.pop('python', None)
        if target_version in matchers:
            jobs.append((name, options))
    return jobs


def read_sections():
    """Read ini files and return list of pairs (name, options)"""
    config = configparser.ConfigParser()
    config.read(('requirements.ini', 'setup.cfg', 'tox.ini'))
    return [
        (
            name,
            {
                key: parse_value(key, config[name][key])
                for key in config[name]
            }
        )
        for name in config.sections()
        if 'requirements' in name
    ]


@lru_cache(maxsize=None)
def _collect_feature_options():
    subclasses = BaseFeature.__subclasses__()
    for feature_class in BaseFeature.__subclasses__():
        subclasses.extend(feature_class.__subclasses__())
    return {
        feature_class.OPTION_NAME: feature_class.CLICK_OPTION
        for feature_class in subclasses
        if feature_class.OPTION_NAME and feature_class.CLICK_OPTION
    }


def parse_value(key, value):
    """Parse value according to the option definition (bool or list)"""
    options = _collect_feature_options()
    click_option = options.get(key)
    if click_option:
        if click_option.multiple:
            return [item.strip() for item in value.split(',')]
        if click_option.is_flag:
            return value.lower() not in ('false', 'off', 'no')
    return value


def python_version_matchers():
    """Return set of string representations of current python version"""
    version = sys.version_info
    patterns = [
        "{0}",
        "{0}{1}",
        "{0}.{1}",
    ]
    matchers = [
        pattern.format(*version)
        for pattern in patterns
    ] + [None]
    return set(matchers)
