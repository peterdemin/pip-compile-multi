Features
--------

``pip-compile-multi`` supports many options to customize compilation.

.. automodule:: pipcompilemulti.features.base_dir

.. automodule:: pipcompilemulti.features.file_extensions

Disable upgrades
================

When new dependencies are added it's tempting to keep everything else the same.
To recompile ``.txt`` keeping satisfying version use ``--no-upgrade``:

.. code-block:: text

    --upgrade / --no-upgrade    Upgrade package version (default true)

The option has no effect if there are no existing ``.txt`` files.

Upgrade only selected packages
==============================

To upgrade only one package and keep everything else untouched, use following option:

.. code-block:: text

    -P, --upgrade-package TEXT  Only upgrade named package.
                                Can be supplied multiple times.

Under the hood it uses
`the same option of pip-compile <https://github.com/jazzband/pip-tools#updating-requirements>`_
and runs compilation only for files that have one of the passed packages.

This option implies ``--no-upgrade`` and takes precedence over ``--upgrade``.

Thanks to `Jonathan Rogers <https://github.com/JonathanRRogers>`_.

.. automodule:: pipcompilemulti.features.use_cache

.. automodule:: pipcompilemulti.features.compatible

Generate hashes
===============

Put package hash after pinned version for additional security.
Format for this option is

.. code-block:: text

  -g, --generate-hashes TEXT  Environment name (base, test, etc.) that needs
                              packages hashes. Can be supplied multiple times.


Example invocation:

.. code-block:: text

    $ pip-compile-multi -g base -g docs

Example output:

.. code-block:: text

    pip-tools==1.11.0 \
        --hash=sha256:50288eb066ce66dbef5401a21530712a93c659fe480c7d8d34e2379300555fa1 \
        --hash=sha256:ba427b68443466c389e3b0b0ef55f537ab39344190ea980dfebb333d0e6a50a3
    first==2.0.1 \
        --hash=sha256:3bb3de3582cb27071cfb514f00ed784dc444b7f96dc21e140de65fe00585c95e \
        --hash=sha256:41d5b64e70507d0c3ca742d68010a76060eea8a3d863e9b5130ab11a4a91aa0e \
        # via pip-tools

``pip`` requires all packages to have hashes if at least one has it.
``pip-compile-multi`` will recursively propagate this option to all environments
that are referencing or referenced by selected environment name.

Custom Header
=============

``pip-compile-multi`` adds a brief header into generated files.
Override it with

.. code-block:: text

    -h, --header TEXT      File path with custom header text for generated files

Limit ``.in`` files
===================

By default ``pip-compile-multi`` compiles all ``.in`` files in ``requirements`` directory.
To limit compilation to only a subset, use

.. code-block:: text

    -n, --only-name TEXT        Compile only for passed environment names and
                                their references. Can be supplied multiple
                                times.

For example, to compile one file under Python2.7 and another under Python3.6, run:

.. code-block:: text

    $ virtual-env27/bin/pip-compile-multi -n deps27
    Locking requirements/deps27.in to requirements/deps27.txt. References: []
    $ virtual-env36/bin/pip-compile-multi -n deps36
    Locking requirements/deps36.in to requirements/deps36.txt. References: []


.. automodule:: pipcompilemulti.features.forbid_post


Check that ``pip-compile-multi`` was run after changes in ``.in`` file.
=======================================================================

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
