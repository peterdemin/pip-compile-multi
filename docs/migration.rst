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
2. Create ``requirements/test.in`` with test time dependencies.
3. Run ``pip-compile-multi``. It will produce two more files:

    * ``requirements/base.txt``
    * ``requirements/test.txt``

4. :ref:`Unpin <unpin>` packages in ``.in`` files.
5. Run ``pip-compile-multi`` again to upgrade the compiled files.

.. _unpin:

How to unpin packages
=====================


