"""Environment discovery"""

import os
import glob

from toposort import toposort_flatten
from .environment import Environment


__all__ = ('discover',)


def discover(glob_pattern):
    """
    Find all files matching given glob_pattern,
    parse them, and return list of environments:

    >>> envs = discover("requirements/*.in")
    >>> # import pprint; pprint.pprint(envs)
    >>> envs == [
    ...     {'name': 'base', 'refs': set()},
    ...     {'name': 'test', 'refs': {'base'}},
    ...     {'name': 'local', 'refs': {'test'}},
    ...     {'name': 'testwin', 'refs': {'test'}},
    ... ]
    True
    """
    in_paths = glob.glob(glob_pattern)
    names = {
        extract_env_name(path): path
        for path in in_paths
    }
    return order_by_refs([
        {'name': name, 'refs': Environment.parse_references(in_path)}
        for name, in_path in names.items()
    ])


def extract_env_name(file_path):
    """Return environment name for given requirements file path"""
    return os.path.splitext(os.path.basename(file_path))[0]


def order_by_refs(envs):
    """
    Return topologicaly sorted list of environments.
    I.e. all referenced environments are placed before their references.
    """
    topology = {
        env['name']: set(env['refs'])
        for env in envs
    }
    by_name = {
        env['name']: env
        for env in envs
    }
    return [
        by_name[name]
        for name in toposort_flatten(topology)
    ]
