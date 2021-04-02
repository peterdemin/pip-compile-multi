"""Functional utilities for lists and dicts manipulation."""

import os
import logging
import itertools


logger = logging.getLogger("pip-compile-multi")


def extract_env_name(file_path):
    """Return environment name for given requirements file path.

    >>> extract_env_name("base.in")
    'base'
    >>> extract_env_name("sub/req.in")
    'req'
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def fix_reference_path(orig_path, ref_path):
    """Find actual path to reference using relative path to original file.

    >>> fix_reference_path("dir/file", "../ref")
    'ref'
    """
    return os.path.normpath(os.path.join(os.path.dirname(orig_path), ref_path))


def recursive_refs(envs, in_path):
    """Return set of recursive refs for given env name."""
    refs_by_in_path = {
        env['in_path']: {
            fix_reference_path(env['in_path'], ref)
            for ref in env['refs']
        }
        for env in envs
    }
    refs = refs_by_in_path[in_path]
    if refs:
        indirect_refs = set(
            subref
            for ref in refs
            for subref in recursive_refs(envs, ref)
        )
    else:
        indirect_refs = set()
    return set.union(refs, indirect_refs)


def merged_packages(env_packages, names):
    """Return union set of environment packages with given names.

    >>> sorted(merged_packages(
    ...     {
    ...         'a': {'x': 1, 'y': 2},
    ...         'b': {'y': 2, 'z': 3},
    ...         'c': {'z': 3, 'w': 4}
    ...     },
    ...     ['a', 'b']
    ... ).items())
    [('x', 1), ('y', 2), ('z', 3)]
    """
    combined_packages = sorted(itertools.chain.from_iterable(
        env_packages[name].items()
        for name in names
    ))
    result = {}
    errors = set()
    for name, version in combined_packages:
        if name in result:
            if result[name] != version:
                errors.add((name, version, result[name]))
        else:
            result[name] = version
    if errors:
        for error in sorted(errors):
            logger.error(
                "Package %s was resolved to different "
                "versions in different environments: %s and %s",
                error[0], error[1], error[2],
            )
        raise RuntimeError(
            "Please add constraints for the package version listed above"
        )
    return result


def reference_cluster(envs, in_path):
    """
    Return set of all env in_paths referencing or
    referenced by given in_path.

    >>> cluster = sorted(reference_cluster([
    ...     {'in_path': 'base', 'refs': []},
    ...     {'in_path': 'test', 'refs': ['base']},
    ...     {'in_path': 'local', 'refs': ['test']},
    ... ], 'test'))
    >>> cluster == ['base', 'local', 'test']
    True
    """
    edges = [
        set([env['in_path'], fix_reference_path(env['in_path'], ref)])
        for env in envs
        for ref in env['refs']
    ]
    prev, cluster = set(), set([in_path])
    while prev != cluster:
        # While cluster grows
        prev = set(cluster)
        to_visit = []
        for edge in edges:
            if cluster & edge:
                # Add adjacent nodes:
                cluster |= edge
            else:
                # Leave only edges that are out
                # of cluster for the next round:
                to_visit.append(edge)
        edges = to_visit
    return cluster
