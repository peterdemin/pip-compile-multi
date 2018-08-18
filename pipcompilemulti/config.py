"""Get tasks options from INI file"""
import sys
import configparser

from .options import OPTIONS


def read_config():
    """Read requirements.ini and return dictionary of section: options"""
    config = configparser.ConfigParser()
    config.read('requirements.ini')
    jobs = []
    matchers = python_version_matchers()
    for section in config.sections():
        target_version = config[section].get('python')
        if target_version in matchers:
            jobs.append((
                section,
                {
                    key: parse_value(key, config[section][key])
                    for key in config[section]
                    if key != 'python'
                }
            ))
    return jobs


def parse_value(key, value):
    """parse value as comma-delimited list if default value for it is list"""
    if isinstance(OPTIONS.get(key), list):
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
    return set([
        pattern.format(*version)
        for pattern in patterns
    ])
