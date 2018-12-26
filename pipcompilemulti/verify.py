"""Verify action"""

import os
import hashlib
import logging

from .options import OPTIONS
from .discover import discover
from .environment import Environment


logger = logging.getLogger("pip-compile-multi")


def verify_environments():
    """
    For each environment verify hash comments and report failures.
    If any failure occured, exit with code 1.
    """
    env_confs = discover(
        os.path.join(
            OPTIONS['base_dir'],
            '*.' + OPTIONS['in_ext'],
        )
    )
    success = True
    for conf in env_confs:
        env = Environment(name=conf['name'])
        current_comment = generate_hash_comment(env.infile)
        existing_comment = parse_hash_comment(env.outfile)
        if current_comment == existing_comment:
            logger.info("OK - %s was generated from %s.",
                        env.outfile, env.infile)
        else:
            logger.error("ERROR! %s was not regenerated after changes in %s.",
                         env.outfile, env.infile)
            logger.error("Expecting: %s", current_comment.strip())
            logger.error("Found:     %s", existing_comment.strip())
            success = False
    return success


def generate_hash_comment(file_path):
    """
    Read file with given file_path and return string of format

        # SHA1:da39a3ee5e6b4b0d3255bfef95601890afd80709

    which is hex representation of SHA1 file content hash
    """
    with open(file_path, 'rb') as fp:
        hexdigest = hashlib.sha1(fp.read().strip()).hexdigest()
    return "# SHA1:{0}\n".format(hexdigest)


def parse_hash_comment(file_path):
    """
    Read file with given file_path line by line,
    return the first line that starts with "# SHA1:", like this:

        # SHA1:da39a3ee5e6b4b0d3255bfef95601890afd80709
    """
    with open(file_path) as fp:
        for line in fp:
            if line.startswith("# SHA1:"):
                return line
    return None
