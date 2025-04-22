Bonus: boilerplate to put in project's README
---------------------------------------------

Nice way of introducing dependency management process to new team members for copy-pasting to `README.md`:

.. code-block:: text

    ## Dependency management

    This project uses [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) for hard-pinning dependencies versions.
    Please see its documentation for usage instructions.
    In short, `requirements/base.in` contains the list of direct requirements with occasional version constraints (like `Django~=4.0`)
    and `requirements/base.txt` is automatically generated from it by adding recursive tree of dependencies with fixed versions.
    The same goes for `test` and `dev`.

    To add a new dependency, add it to the appropriate environment's `in` file,
    (e.g. `requirements/base.in`) and run `pip-compile-multi --no-upgrade`.
    To upgrade dependency versions, run `pip-compile-multi`.

    For installation always use `.txt` files. For example, command `pip install -e . -r requirements/dev.txt` will install
    this project in development mode, testing requirements and development tools.
    Another useful command is `pip-sync requirements/dev.txt`, it uninstalls packages from your virtualenv that aren't listed in the file.

If project is using the second-generation ``requirements`` CLI:

.. code-block:: text

    ## Dependency management

    This project uses [pip-compile-multi](https://pypi.org/project/pip-compile-multi/) for hard-pinning dependencies versions.
    Please see its documentation for usage instructions.
    In short, `requirements/base.in` contains the list of direct requirements with occasional version constraints (like `Django~=4.0`)
    and `requirements/base.txt` is automatically generated from it by adding recursive tree of dependencies with fixed versions.
    The same goes for `test` and `dev`.

    To add a new dependency, add it to the appropriate environment's `in` file,
    (e.g. `requirements/base.in`) and run `requirements lock`.
    To upgrade dependency versions, run `requirements upgrade`.

    For installation always use `.txt` files. For example, command `pip install -Ue . -r requirements/dev.txt` will install
    this project in development mode, testing requirements and development tools.
    Another useful command is `pip-sync requirements/dev.txt`, it uninstalls packages from your virtualenv that aren't listed in the file.
