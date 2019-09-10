Features
--------

``pip-compile-multi`` supports many options to customize compilation.

.. automodule:: pipcompilemulti.features.base_dir

.. automodule:: pipcompilemulti.features.file_extensions

.. automodule:: pipcompilemulti.features.upgrade

.. automodule:: pipcompilemulti.features.use_cache

.. automodule:: pipcompilemulti.features.compatible

.. automodule:: pipcompilemulti.features.add_hashes

Custom Header
=============

``pip-compile-multi`` adds a brief header into generated files.
Override it with

.. code-block:: text

    -h, --header TEXT      File path with custom header text for generated files

.. automodule:: pipcompilemulti.features.limit_envs


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
