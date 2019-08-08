Motivation
----------

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

That's great, and solves the main problem - service will be deployed exactly [1]_
the same every single time and all developers will have same environments.

This case is so common that there already are some tools to solve it.
Two worth mentioning are:

1. `Pip Tools`_ - a mature package that is enhanced by ``pip-compile-multi``.
2. `PipEnv`_ - a fresh approach that is going to become the "official" Python way of locking dependencies some day.

.. _Pip Tools: https://github.com/jazzband/pip-tools
.. _PipEnv: https://github.com/pypa/pipenv

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

.. [1] That's not true.
       Someone could re-upload broken package under existing version on PyPI.
       For 100% reproducible builds use hashes.
