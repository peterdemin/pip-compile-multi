#!/usr/bin/env python
"""High level actions to be called from CLI"""

from .discover import discover
from .environment import Environment
from .verify import generate_hash_comment
from .features import FEATURES
from .deduplicate import PackageDeduplicator


def recompile():
    """Compile requirements files for all environments."""
    env_confs = discover(FEATURES.compose_input_file_path('*'))
    FEATURES.on_discover(env_confs)
    deduplicator = PackageDeduplicator()
    deduplicator.on_discover(env_confs)
    for conf in env_confs:
        if not FEATURES.included(conf['name']):
            continue
        env = Environment(name=conf['name'], deduplicator=deduplicator)
        if env.maybe_create_lockfile():
            # Only munge lockfile if it was written.
            header_text = generate_hash_comment(env.infile) + FEATURES.get_header_text()
            env.replace_header(header_text)
            env.add_references(conf['refs'])
