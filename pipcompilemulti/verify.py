"""
Check that ``pip-compile-multi`` was run after changes in ``.in`` file
======================================================================

``pip-compile-multi`` adds a special line (before header) at the beginning of each generated file.
This line contains a SHA1 hash of the ``.in`` file's contents.

Command

.. code-block:: shell

    $ pip-compile-multi verify
    OK - requirements/base.txt was generated from requirements/base.in.
    OK - requirements/test.txt was generated from requirements/test.in.
    OK - requirements/local.txt was generated from requirements/local.in.
    OK - requirements/testwin.txt was generated from requirements/testwin.in.

Or, if using ``requirements`` command:

.. code-block:: shell

    $ requirements verify
    OK - requirements/base.txt was generated from requirements/base.in.
    OK - requirements/test.txt was generated from requirements/test.in.
    OK - requirements/local.txt was generated from requirements/local.in.
    OK - requirements/testwin.txt was generated from requirements/testwin.in.
    OK - requirements/base.hash was generated from requirements/base.txt.
    OK - requirements/test.hash was generated from requirements/test.txt.
    OK - requirements/local.hash was generated from requirements/local.txt.
    OK - requirements/testwin.hash was generated from requirements/testwin.txt.


recalculates hashes for ``.in`` files and compares them with the stored values.

If verification fails, an error message is logged and exit code 1 is returned:

.. code-block:: shell

    $ pip-compile-multi verify
    ERROR! requirements/base.txt was not regenerated after changes in requirements/base.in.
    Expecting: # SHA1:7d82ce5a82b0a6cf91b2c4debe90eb1e5ef37f37
    Found:     # SHA1:32737333f763ceffd22b7fcb76fbe62a538296fa
    OK - requirements/test.txt was generated from requirements/test.in.
    OK - requirements/local.txt was generated from requirements/local.in.
    OK - requirements/testwin.txt was generated from requirements/testwin.in.


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
        env = Environment(in_path=conf['in_path'])
        current_comment = generate_hash_comment(env.infile)
        robust_comment = generate_robust_hash_comment(env.infile)
        existing_comment = parse_hash_comment(env.outfile)
        if existing_comment in (robust_comment, current_comment):
            logger.info("OK - %s was generated from %s.",
                        env.outfile, env.infile)
        else:
            logger.error("ERROR! %s was not regenerated after changes in %s.",
                         env.outfile, env.infile)
            logger.error("Expecting: %s", robust_comment.strip())
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
    return f"# SHA1:{hexdigest}\n"


def generate_robust_hash_comment(file_path):
    """
    Read file with given file_path and return string of format

        # SHA1:da39a3ee5e6b4b0d3255bfef95601890afd80709

    which is hex representation of SHA1 file content hash.
    File content is pre-processed by stripping comments, whitespace and newlines.
    """
    with open(file_path, 'rt', encoding="utf-8") as fp:
        essense = ''.join(sorted(
            line.split('#')[0].strip()
            for line in fp
        ))
    hexdigest = hashlib.sha1(essense.encode("utf-8")).hexdigest()
    return f"# SHA1:{hexdigest}\n"


def parse_hash_comment(file_path):
    """
    Read file with given file_path line by line,
    return the first line that starts with "# SHA1:", like this:

        # SHA1:da39a3ee5e6b4b0d3255bfef95601890afd80709
    """
    with open(file_path, encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("# SHA1:"):
                return line
    return ''
