===============================
pip-compile-multi
===============================

.. image:: https://badge.fury.io/py/pip-compile-multi.png
    :target: http://badge.fury.io/py/pip-compile-multi

.. image:: https://travis-ci.org/peterdemin/pip-compile-multi.svg?branch=master
    :target: https://travis-ci.org/peterdemin/pip-compile-multi

.. image:: https://ci.appveyor.com/api/projects/status/1spvqh9hlqtv2a81?svg=true
    :target: https://ci.appveyor.com/project/peterdemin/pip-compile-multi

.. image:: https://img.shields.io/pypi/pyversions/pip-compile-multi.svg
    :target: https://pypi.python.org/pypi/pip-compile-multi


Compile multiple requirements files to lock dependency versions

Installation
------------

.. code-block:: shell

    pip install pip-compile-multi

Basic Usage
-----------

.. code-block:: shell

    pip-compile-multi

Example scenario
----------------

I will start from the very basics of dependency management and will go very slow,
so if you feel bored, just scroll to the next section.

Suppose you have a python project with following direct dependencies:

.. code-block:: text

    click
    pip-tools

(Yes I took pip-compile-multi as an example).
Let's save them as-is in ``requirements/base.in``.
Those are unpinned libraries. It means that whenever developer runs

.. code-block:: shell

    pip install -r requirements/base.in

they will get *some* version of these libraries.
And the chances are that if several developers do the same over some period,
some will have different dependency versions than others.
Also, if the project is online service, one day it may stop working after
redeployment because some of the dependencies had backward incompatible release.
These backward incompatible changes are relatively common.

To avoid this problem, Python developers are hard-pinning (aka locking) their dependencies.
So instead of a list of libraries, they have something like:

.. code-block:: text

    click==6.7
    pip-tools==1.11.0

(To keep things neat let's put this into ``requirements/base.txt``)
That's good for a starter. But there are two significant drawbacks:

1. Developers have to do non-trivial operations if they want to keep up with
   newer versions (that have bug fixes and performance improvements).
2. Indirect dependencies (that is dependencies of dependencies) may still have
   backward-incompatible releases, that break everything.

Let's put aside point 1 and fight point 2. Let's do

.. code-block:: shell

    pip freeze > requirements/base.txt

Now we have full hierarchy of dependencies hard-pinned:

.. code-block:: text

    click==6.7
    first==2.0.1
    pip-tools==1.11.0
    six==1.11.0

That's great, and solves the main problem - service will be deployed exactly [1]
the same every single time and all developers will have same environments.

This case is so common that there already are some tools to solve it.
Two worth mentioning are:

1. `Pip Tools`_ - a mature package that is enhanced by ``pip-compile-multi``.
2. `PipEnv`_ - a fresh approach that is going to become the "official" Python way of locking dependencies some day.

But what if the project uses some packages that are not required by the service itself?
For example ``pytest``, that is needed to run unit tests, but should never
be deployed to a production site. Or ``flake8`` - syntax checking tool.
If they are installed in the current virtual environment, they will get into
``pip freeze`` output.
That's no good.
And removing them manually from ``requirements/base.txt`` is not an option.
But still, these packages must be pinned to ensure, that tests are running
the same way on all development machines (and build server).

So let's get hands dirty and put all the testing stuff into ``requirements/test.in``:

.. code-block:: text

    -r base.in

    prospector
    pylint
    flake8
    mock
    six

Note, how I put ``-r base.in`` in the beginning, so that *test* dependencies are installed
along with the *base*.

Now installation command is

.. code-block:: shell

    pip install -e requirements/test.in

For one single time (exceptionally to show how unacceptable is this task)
let's manually compose ``requirements/test.txt``.
After installation, run freeze to bring the whole list of all locked packages:

.. code-block:: shell

    $ pip freeze
    astroid==1.6.0
    click==6.7
    dodgy==0.1.9
    first==2.0.1
    flake8==3.5.0
    flake8-polyfill==1.0.2
    isort==4.2.15
    lazy-object-proxy==1.3.1
    mccabe==0.6.1
    mock==2.0.0
    pbr==3.1.1
    pep8-naming==0.5.0
    pip-tools==1.11.0
    prospector==0.12.7
    pycodestyle==2.0.0
    pydocstyle==2.1.1
    pyflakes==1.6.0
    pylint==1.8.1
    pylint-celery==0.3
    pylint-common==0.2.5
    pylint-django==0.7.2
    pylint-flask==0.5
    pylint-plugin-utils==0.2.6
    PyYAML==3.12
    requirements-detector==0.5.2
    setoptconf==0.2.0
    six==1.11.0
    snowballstemmer==1.2.1
    wrapt==1.10.11

Wow! That's quite a list! But we remember what goes into base.txt:

1. click
2. first
3. pip-tools
4. six

Good, everything else can be put into ``requirements/test.txt``.
But wait, ``six`` is included in ``test.in`` and is missing in ``test.txt``.
That feels wrong. Ah, it's because we've moved ``six`` to the ``base.txt``.
It's good that we didn't forget, that it should be in *base*.
We might forget next time though.

Why don't we automate it? That's what ``pip-compile-multi`` is for.

Managing dependency versions in multiple environments
-----------------------------------------------------

Let's rehearse. Example service has two groups of dependencies
(or, as I call them, environments):

.. code-block:: shell

    $ cat requirements/base.in
    click
    pip-tools

    $ cat requirements/test.in
    -r base.in
    prospector
    pylint
    flake8
    mock
    six

To make automation even more appealing, let's add one more environment.
I'll call it *local* - things that are needed during development, but are not
required by tests, or service itself.

.. code-block:: shell

    $ cat requirements/local.in
    -r test.in
    tox

Now we want to put all *base* dependencies along with all their recursive dependencies
in ``base.txt``,
all recursive *test* dependencies except for *base* into ``test.txt``,
and all recursive *local* dependencies except for *base* and *test* into ``local.txt``.

.. code-block:: shell

    $ pip-compile-multi
    Locking requirements/base.in to requirements/base.txt. References: []
    Locking requirements/test.in to requirements/test.txt. References: ['base']
    Locking requirements/local.in to requirements/local.txt. References: ['base', 'test']

Yes, that's right. All the tedious dependency versions management job done with
a single command that doesn't even have options.

Now you can run ``git diff`` to review the changes and ``git commit`` to save them.
To install the new set of versions run:

.. code-block:: shell

    pip install -Ur requirements/local.txt

It's a perfect time to run all the tests and make sure, that updates were
backward compatible enough for your needs.
More often than I'd like in big projects, it's not so.
Let's say the new version of ``pylint`` dropped support of old Python version,
that you still need to support.
Than you open ``test.in`` and soft-pin it with descriptive comment:

.. code-block:: shell

    $ cat requirements/test.in
    -r base.in
    prospector
    pylint<1.8  # Newer versions dropped support for Python 2.4
    flake8
    mock
    six

I know, this example is made up. But you get the idea.
That re-run ``pip-compile-multi`` to compile new ``test.txt`` and check new set.

Benefits of using pip-compile-multi
-----------------------------------

I want to summarise, why ``pip-compile-multi`` might be a good addition to your project.
Some of the benefits are achievable with other methods, but I want to be general:

1. Production will not suddenly break after redeployment because of
   backward incompatible dependency release.
2. Every development machine will have the same package versions.
3. Service still uses most recent versions of packages.
   And fresh means best here.
4. Dependencies are upgraded when the time is suitable for the service,
   not whenever they are released.
5. Different environments are separated into different files.
6. ``*.in`` files are small and manageable because they store only direct dependencies.
7. ``*.txt`` files are exhaustive and precise (but you don't need to edit them).

Features
--------

``pip-compile-multi`` supports many options to customize compilation.

Requirements Directory
======================

While it's a common practice to put requirements files inside ``requirements`` directory,
it's not always the case. The directory can be overridden with this option:

.. code-block:: text

    -d, --directory TEXT   Directory path with requirements files

Requirements Files Extensions
=============================

By default ``pip-compile-multi`` compiles ``*.txt`` from ``*.in`` files.
While this is a common naming pattern, each project can use it's own:

.. code-block:: text

    -i, --in-ext TEXT      File extension of input files
    -o, --out-ext TEXT     File extension of output files

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

Compatible Releases
===================

`PEP-440`_ describes compatible release operator ``~=``.
Sometimes it's useful to have some of the dependencies pinned using this operator.
For example, rapidly changing internal libraries.
The format for this option is

.. code-block:: text

    -c, --compatible TEXT

where TEXT is a `glob`_ pattern for library name.
This option can be supplied multiple times.


.. _glob: https://en.wikipedia.org/wiki/Glob_(programming)
.. _PEP-440: https://www.python.org/dev/peps/pep-0440/#compatible-release

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

Forbid .postX release
=====================

``pip-compile-multi`` can remove ``.postX`` part of dependencies versions.

.. code-block:: text

    -p, --forbid-post TEXT      Environment name (base, test, etc) that cannot
                                have packages with post-release versions
                                (1.2.3.post777). Can be supplied multiple times.

Be careful with this option since different maintainers treat post releases differently.

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

Verify as pre-commit hook
=========================

To verify that ``pip-compile-multi`` has been run after changing ``.in`` files as a `PreCommit`_ hook, just add the following to your local repo's ``.pre-commit-config.yaml`` file:

.. code-block:: yaml

    - repo: https://github.com/peterdemin/pip-compile-multi
      rev: v1.3.2
      hooks:
        - id: pip-compile-multi-verify

Bonus: boilerplate to put in project's README
---------------------------------------------

Nice way of introducing dependency management process to new team members for copy-pasting to `README.md`:

.. code-block:: text

    ## Dependency management

    This project uses [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) for hard-pinning dependencies versions.
    Please see its documentation for usage instructions.
    In short, `requirements/base.in` contains the list of direct requirements with occasional version constraints (like `Django<2`)
    and `requirements/base.txt` is automatically generated from it by adding recursive tree of dependencies with fixed versions.
    The same goes for `test` and `dev`.

    To upgrade dependency versions, run `pip-compile-multi`.

    To add a new dependency without upgrade, add it to `requirements/base.in` and run `pip-compile-multi --no-upgrade`.

    For installation always use `.txt` files. For example, command `pip install -Ue . -r requirements/dev.txt` will install
    this project in development mode, testing requirements and development tools.
    Another useful command is `pip-sync requirements/dev.txt`, it uninstalls packages from your virtualenv that aren't listed in the file.


Have fun!
---------

Now that occasional backward incompatible dependency release can't ruin your day,
you can **spread the word** about ``pip-compile-multi``, ask for a new feature in a `GitHub issue`_,
or even open a PR ;-).

[1] That's not true. Someone could re-upload broken package
under existing version on PyPI.

.. _Pip Tools: https://github.com/jazzband/pip-tools
.. _PipEnv: https://github.com/pypa/pipenv
.. _GitHub issue: https://github.com/peterdemin/pip-compile-multi/issues
.. _PreCommit: https://pre-commit.com/
