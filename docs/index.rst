.. pip-compile-multi documentation master file, created by
   sphinx-quickstart on Thu Aug  8 15:36:37 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pip-compile-multi
~~~~~~~~~~~~~~~~~

Pip-compile-multi is a command line utility, that compiles multiple
requirements files to lock dependency versions.
Underneath it uses `pip-tools`_ for actual compilation.
Pip-compile-multi targets complex projects and provides highest
level of automation and flexibility in class.

.. _pip-tools: https://github.com/jazzband/pip-tools

To install:

.. code-block:: shell

    pip install pip-compile-multi

To run:

.. code-block:: shell

    pip-compile-multi


Why use pip-compile-multi?
==========================

.. toctree::
    :maxdepth: 2

    why


How to use pip-compile-multi?
=============================

.. toctree::
    :maxdepth: 2

    installation
    migration
    features
    precommit
    boilerplate


Release notes
=============

.. toctree::
    :maxdepth: 2

    history


.. include:: afterword.rst
