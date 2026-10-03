============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/peterdemin/pip-compile-multi/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

pip-compile-multi could always use more documentation, whether as part of the
official pip-compile-multi docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/peterdemin/pip-compile-multi/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `pip-compile-multi` for local development.

1. Fork the `pip-compile-multi` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/pip-compile-multi.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv pip-compile-multi
    $ cd pip-compile-multi/
    $ make install

   This installs the versions locked in ``requirements/local.hash`` and the
   local package. Use ``make sync`` to synchronize an existing environment
   with ``uv pip sync`` and hash verification, then reinstall the local package.
   With this virtualenv activated, install and run the commit hooks::

    $ pre-commit install
    $ pre-commit run --all-files

   Hooks use ``repo: local`` and ``language: system`` to run ``python -m ...``
   from the active virtualenv. Keep it activated when committing; pre-commit
   does not create separate tool environments or download other tool versions.

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, run lint, strict type checking, and the tests
   with tox::

    $ tox -e lint,typing
    $ tox

   Install tox in your virtualenv; it installs the tools for each environment.
   The lint environment runs Ruff, isort (with the Black profile), Black, and
   pylint. To apply safe lint fixes, sort imports, and format locally::

    $ python -m ruff check --fix .
    $ python -m isort .
    $ python -m black --config black.toml .

   The typing environment checks the package with strict mypy, strict Pyright,
   and Astral's ty, targeting Python 3.10. Configuration lives in ``setup.cfg``,
   ``pyrightconfig.json``, ``ruff.toml``, ``black.toml``, and ``ty.toml``.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.10 and newer, including compatible
   PyPy versions. Check GitHub Actions and make sure the tests and type checks pass.

Tips
----

To run a subset of tests::

    TODO
