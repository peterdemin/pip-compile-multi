#!/usr/bin/env python
"""High level actions to be called from CLI"""

import logging
import itertools

from .discover import discover
from .environment import Environment
from .verify import generate_hash_comment
from .features import FEATURES
from .features.limit_envs import recursive_refs


logger = logging.getLogger("pip-compile-multi")


def recompile():
    """Compile requirements files for all environments."""
    pinned_packages = {}
    env_confs = discover(FEATURES.compose_input_file_path('*'))
    FEATURES.on_discover(env_confs)
    for conf in env_confs:
        if not FEATURES.included(conf['name']):
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
            header_text = generate_hash_comment(env.infile) + FEATURES.get_header_text()
            env.replace_header(header_text)
            env.add_references(conf['refs'])
        pinned_packages[conf['name']] = env.packages


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
