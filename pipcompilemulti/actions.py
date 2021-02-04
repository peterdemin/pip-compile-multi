#!/usr/bin/env python
"""High level actions to be called from CLI"""

import logging

from .discover import discover
from .environment import Environment
from .verify import generate_robust_hash_comment
from .features import FEATURES
from .deduplicate import PackageDeduplicator


logger = logging.getLogger("pip-compile-multi")


def recompile():
    """Compile requirements files for all environments."""
    env_confs = discover(FEATURES.compose_input_file_path('*'))
    FEATURES.on_discover(env_confs)
    deduplicator = PackageDeduplicator()
    deduplicator.on_discover(env_confs)
    sink_in_path = FEATURES.sink_in_path()
    if sink_in_path:
        sink_env = Environment(in_path=sink_in_path)
        logger.info(
            "Creating a temporary file with all dependencies at %s",
            sink_env.outfile,
        )
        sink_env.create_lockfile()
    compile_topologically(env_confs, deduplicator)


def compile_topologically(env_confs, deduplicator):
    """Compile environments in topological order of reference."""
    for conf in env_confs:
        if not FEATURES.included(conf['in_path']):
            continue
        env = Environment(in_path=conf['in_path'], deduplicator=deduplicator)
        if env.maybe_create_lockfile():
            # Only munge lockfile if it was written.
            header_text = generate_robust_hash_comment(env.infile) + FEATURES.get_header_text()
            env.replace_header(header_text)
            env.add_references(conf['refs'])
