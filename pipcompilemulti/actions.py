#!/usr/bin/env python
"""High level actions to be called from CLI"""

import os
import logging
import itertools

from .options import OPTIONS, DEFAULT_HEADER
from .discover import discover
from .environment import Environment
from .verify import generate_hash_comment


logger = logging.getLogger("pip-compile-multi")


def recompile():
    """
    Compile requirements files for all environments.
    """
    pinned_packages = {}
    env_confs = discover(
        os.path.join(
            OPTIONS['base_dir'],
            '*.' + OPTIONS['in_ext'],
        ),
    )
    if OPTIONS['header_file']:
        with open(OPTIONS['header_file']) as fp:
            base_header_text = fp.read()
    else:
        base_header_text = DEFAULT_HEADER
    hashed_by_reference = set()
    for name in OPTIONS['add_hashes']:
        hashed_by_reference.update(
            reference_cluster(env_confs, name)
        )
    included_and_refs = set(OPTIONS['include_names'])
    for name in set(included_and_refs):
        included_and_refs.update(
            recursive_refs(env_confs, name)
        )
    for conf in env_confs:
        if included_and_refs:
            if conf['name'] not in included_and_refs:
                # Skip envs that are not included or referenced by included:
                continue
        rrefs = recursive_refs(env_confs, conf['name'])
        add_hashes = conf['name'] in hashed_by_reference
        env = Environment(
            name=conf['name'],
            ignore=merged_packages(pinned_packages, rrefs),
            forbid_post=conf['name'] in OPTIONS['forbid_post'],
            add_hashes=add_hashes,
        )
        logger.info("Locking %s to %s. References: %r",
                    env.infile, env.outfile, sorted(rrefs))
        if env.maybe_create_lockfile():
            # Only munge lockfile if it was written.
            header_text = generate_hash_comment(env.infile) + base_header_text
            env.replace_header(header_text)
            env.add_references(conf['refs'])

        pinned_packages[conf['name']] = env.packages


def merged_packages(env_packages, names):
    """
    Return union set of environment packages with given names

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


def recursive_refs(envs, name):
    """
    Return set of recursive refs for given env name

    >>> local_refs = sorted(recursive_refs([
    ...     {'name': 'base', 'refs': []},
    ...     {'name': 'test', 'refs': ['base']},
    ...     {'name': 'local', 'refs': ['test']},
    ... ], 'local'))
    >>> local_refs == ['base', 'test']
    True
    """
    refs_by_name = {
        env['name']: set(env['refs'])
        for env in envs
    }
    refs = refs_by_name[name]
    if refs:
        indirect_refs = set(itertools.chain.from_iterable([
            recursive_refs(envs, ref)
            for ref in refs
        ]))
    else:
        indirect_refs = set()
    return set.union(refs, indirect_refs)


def reference_cluster(envs, name):
    """
    Return set of all env names referencing or
    referenced by given name.

    >>> cluster = sorted(reference_cluster([
    ...     {'name': 'base', 'refs': []},
    ...     {'name': 'test', 'refs': ['base']},
    ...     {'name': 'local', 'refs': ['test']},
    ... ], 'test'))
    >>> cluster == ['base', 'local', 'test']
    True
    """
    edges = [
        set([env['name'], ref])
        for env in envs
        for ref in env['refs']
    ]
    prev, cluster = set(), set([name])
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
