"""Get tasks options from INI file"""
import sys
import configparser

from .options import OPTIONS


def read_config():
    """Read requirements.ini and return dictionary of section: options
    If no requirements sections found, return None.
    If some sections found, but none matches current runtime, return empty list.
    """
    config = configparser.ConfigParser()
    config.read(('requirements.ini', 'setup.cfg', 'tox.ini'))
    jobs = []
    use_default = True
    matchers = python_version_matchers()
    for section in config.sections():
        if 'requirements' in section:
            use_default = False
        else:
            continue
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
    if use_default:
        return None
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
    matchers = [
        pattern.format(*version)
        for pattern in patterns
    ]
    return set(matchers)
