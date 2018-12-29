"""Get tasks options from INI file"""
import sys
import configparser


PREFIX = 'requirements:'


def read_config():
    """Read requirements.ini and return filtered
    list of pairs (name, options).

    If no requirements sections found, return None.
    If some sections found, but none matches current runtime,
    return empty list.
    """
    return filter_sections(read_sections())


def filter_sections(sections):
    """Filter through pairs (name, options)
    leaving only those that match runtime.

    If no requirements sections found, return None.
    If some sections found, but none matches current runtime,
    return empty list.
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
        (name, dict(config[name].items()))
        for name in config.sections()
        if name.startswith(PREFIX)
    ]


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
