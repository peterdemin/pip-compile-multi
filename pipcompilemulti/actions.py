#!/usr/bin/env python
"""High level actions to be called from CLI"""

import logging
import itertools

from .options import OPTIONS, DEFAULT_HEADER
from .discover import discover
from .environment import Environment
from .verify import generate_hash_comment
from .features import FEATURES


logger = logging.getLogger("pip-compile-multi")


def recompile():
    """
    Compile requirements files for all environments.
    """
    pinned_packages = {}
    env_confs = discover(FEATURES.compose_input_file_path('*'))
    FEATURES.on_discover(env_confs)
    if OPTIONS['header_file']:
        with open(OPTIONS['header_file']) as fp:
            base_header_text = fp.read()
    else:
        base_header_text = DEFAULT_HEADER
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
        env = Environment(
            name=conf['name'],
            ignore=merged_packages(pinned_packages, rrefs),
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
