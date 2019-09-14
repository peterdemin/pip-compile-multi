"""
Check that ``pip-compile-multi`` was run after changes in ``.in`` file
======================================================================

``pip-compile-multi`` adds a special line (before header) at the beginning of each generated file.
This line contains a SHA1 hash of the ``.in`` file's contents.

Command

.. code-block:: shell

    $ pip-compile-multi verify
    Verifying that requirements/base.txt was generated from requirements/base.in.
    Success - comments match.
    Verifying that requirements/test.txt was generated from requirements/test.in.
    Success - comments match.
    Verifying that requirements/local.txt was generated from requirements/local.in.
    Success - comments match.

recalculates hashes for ``.in`` files and compares them with the stored values.

If verification fails, an error message is logged and exit code 1 is returned:

.. code-block:: shell

    $ pip-compile-multi verify
    Verifying that requirements/base.txt was generated from requirements/base.in.
    Success - comments match.
    Verifying that requirements/test.txt was generated from requirements/test.in.
    FAILURE!
    Expecting: # SHA1:c93d71964e14b04f3c8327d16dbc4d6b1bbc3b1d
    Found:     # SHA1:6c2562322ca1bdc8309b08581a2aa4efbb5a4534
    Verifying that requirements/local.txt was generated from requirements/local.in.
    Success - comments match.


In big teams it might be a good idea to have this check in ``tox.ini``:

.. code-block:: ini

    [testenv:verify]
    skipsdist = true
    skip_install = true
    deps = pip-compile-multi
    commands = pip-compile-multi verify
    whitelist_externals = pip-compile-multi
"""

import hashlib
import logging

from .discover import discover
from .environment import Environment
from .features import FEATURES


logger = logging.getLogger("pip-compile-multi")


def verify_environments():
    """
    For each environment verify hash comments and report failures.
    If any failure occured, exit with code 1.
    """
    env_confs = discover(FEATURES.compose_input_file_path('*'))
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
    return ''
