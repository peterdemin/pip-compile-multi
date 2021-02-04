"""Environment discovery"""

import glob
from collections import deque

from toposort import toposort_flatten
from .environment import Environment
from .utils import fix_reference_path, extract_env_name


__all__ = ('discover',)


def discover(glob_pattern):
    """
    Find all files matching given glob_pattern,
    parse them, and return list of environments:

    Recursively follow referenced files not matched by glob_pattern.

    >>> import os
    >>> envs = discover(os.path.join('requirements', '*.in'))
    >>> # import pprint; pprint.pprint(envs)
    >>> envs == [
    ...  {'in_path': os.path.join('requirements', 'base.in'), 'name': 'base',
    ...   'refs': set()},
    ...  {'in_path': os.path.join('requirements', 'test.in'), 'name': 'test',
    ...   'refs': {'base.in'}},
    ...  {'in_path': os.path.join('requirements', 'local.in'), 'name': 'local',
    ...   'refs': {'test.in'}},
    ...  {'in_path': os.path.join('requirements', 'testwin.in'), 'name': 'testwin',
    ...   'refs': {'test.in'}}
    ... ]
    True
    """
    to_visit = deque(glob.glob(glob_pattern))
    envs, all_in_paths = {}, set()
    while to_visit:
        in_path = to_visit.pop()
        # name =
        if in_path in all_in_paths:
            continue
        all_in_paths.add(in_path)
        envs[in_path] = {
            'in_path': in_path,
            'name': extract_env_name(in_path),
            'refs': Environment.parse_references(in_path),
        }
        for ref in envs[in_path]['refs']:
            to_visit.append(fix_reference_path(
                orig_path=in_path,
                ref_path=ref
            ))
    return order_by_refs(envs.values())


def order_by_refs(envs):
    """Return topologicaly sorted list of environments.

    I.e. all referenced environments are placed before their references.
    """
    topology = {
        env['in_path']: set(fix_reference_path(env['in_path'], ref)
                            for ref in env['refs'])
        for env in envs
    }
    by_in_path = {
        env['in_path']: env
        for env in envs
    }
    return [
        by_in_path[in_path]
        for in_path in toposort_flatten(topology)
    ]
