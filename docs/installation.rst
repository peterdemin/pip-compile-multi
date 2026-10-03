Installation
------------

Python Version
==============

We recommend using the latest version of Python 3.
Pip-compile-multi supports Python 3.10 and newer, including compatible PyPy versions.

Dependencies
============

These distributions will be installed automatically when installing pip-compile-multi.

* `Click`_ is a framework for writing command line applications.
* `pip-tools`_ is a set of command line tools to help you keep your pip-based
  packages fresh, even when you've pinned them.
* `toposort`_ implements topological sort algorithm. Pip-compile-multi uses it
  to compose compilation order of requirements files.

.. _Click: https://palletsprojects.com/p/click/
.. _pip-tools: https://github.com/jazzband/pip-tools
.. _toposort: https://pypi.org/project/toposort/

Virtual environments
====================

Use a virtual environment to manage the dependencies for your project, both in
development and in production.

What problem does a virtual environment solve? The more Python projects you
have, the more likely it is that you need to work with different versions of
Python libraries, or even Python itself. Newer versions of libraries for one
project can break compatibility in another project.

Virtual environments are independent groups of Python libraries, one for each
project. Packages installed for one project will not affect other projects or
the operating system's packages.

Python comes bundled with the :mod:`venv` module to create virtual environments.

.. _install-create-env:

Create an environment
~~~~~~~~~~~~~~~~~~~~~

Create a project folder and a :file:`venv` folder within:

.. code-block:: sh

    $ mkdir myproject
    $ cd myproject
    $ python3 -m venv venv

On Windows:

.. code-block:: bat

    $ py -3 -m venv venv

.. _install-activate-env:

Activate the environment
~~~~~~~~~~~~~~~~~~~~~~~~

Before you work on your project, activate the corresponding environment:

.. code-block:: sh

    $ . venv/bin/activate

On Windows:

.. code-block:: bat

    > venv\Scripts\activate

Your shell prompt will change to show the name of the activated environment.

Install pip-compile-multi
=========================

Within the activated environment, use the following command to install pip-compile-multi:

.. code-block:: shell

    pip install pip-compile-multi

pip-compile-multi is now installed. Check out the :doc:`/features` or go to the
:doc:`Documentation Overview </index>`.
