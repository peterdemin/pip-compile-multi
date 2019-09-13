"""Get tasks options from INI file"""
import sys
import configparser

from .options import LIST_OPTIONS


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


def parse_value(key, value):
    """Parse value as comma-delimited list if key is in LIST_OPTIONS"""
    if key in LIST_OPTIONS:
        return [item.strip()
                for item in value.split(',')]
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
