How to start using pip-compile-multi on existing project
--------------------------------------------------------

Initial situation
=================

There are various ways to declare dependencies in Python project.
The most straightforward is to just put them right into ``setup.py``,
like `Flask`_ does.
Another common option is to have one or more ``requirements.txt`` files in a project,
like `Deluge`_ have.

.. _Flask: https://github.com/pallets/flask/blob/master/setup.py#L52-L75
.. _Deluge: https://github.com/deluge-torrent/deluge/blob/develop/requirements.txt


Migration steps
===============

1. Create ``requirements`` directory.
2. Copy-paste the list of project runtime dependencies
   to ``requirements/base.in``.
3. Create ``requirements/test.in`` with test time dependencies.
   Make sure it has a reference to runtime dependencies - ``-r base.in``.
4. Run ``pip-compile-multi``. It will produce two more files:

    * ``requirements/base.txt``
    * ``requirements/test.txt``

5. :ref:`Unpin <unpin>` packages in ``.in`` files.
6. Run ``pip-compile-multi`` again to upgrade the compiled files.

.. _unpin:

How to unpin packages
=====================

No constraints
~~~~~~~~~~~~~~

Some projects don't constraint it's dependencies. In this case, there's nothing to unpin, no more work needed.

Hard-pinned versions (==)
~~~~~~~~~~~~~~~~~~~~~~~~~

Some projects hard-pin all dependencies, just to be safe.
Most likely, the code will run fine with the next patch release, but it's hard to tell for sure.
For such cases, comprehensive test suite is vital.

Your milage may vary, but generally the fastest workflow is as follows:

1. Remove all the constraints, by deleting everything after package names (e.g. ``==1.2.3``).
2. Recompile ``.txt`` requirements.
3. Install new versions.
4. Run tests.
5. If tests passed, job's done.
6. If some of the tests fails, it's likely that some of the original constraints
   was indeed required. Try to find what's the incompatible package version, maybe read package's CHANGELOG.
   Maybe the simpliest way is to return whatever constraint was originally set to move the needle.
7. After updating one of the ``.in`` files, go to step 2.

Two-way constraints (>1,<2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The popular requirements policy is to add packages constrained to minor releases, like this::

	uwsgi>2.0.0,<2.1.0

The idea is that dependency is following SemVer and patch release won't break any functionality.
Of course, the reality is that some times patch release introduces a bug,
and some times next major release is backwards compatible.
But looking at this line you can't tell if ``uwsgi==2.1.0`` is going to break your app.
The only way to know it is to actually try.

So for such projects the general approach is to remove all ``<`` constraints and see
which of them were really needed.
