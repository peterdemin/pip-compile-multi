# Managing dependencies in multi-platform Python project

I'm going to describe the setup I made for my Python
[project](https://github.com/peterdemin/pip-compile-multi).

The project supports Python version 2.7 and 3.4+, PyPy, Linux, and Windows.
It runs tests on every commit in Travis CI and AppVeyor.
The project relies on a few runtime packages (5),
a bunch for testing (12) and a lot for development (36).
Some dependencies are shared, some specific to Python 2.7 and some to Windows.

The project uses hard-pinned packages with hashes to verify the integrity of installed versions.

## Problems

Let's summarize what we are solving:

1. The project has 3 set of dependencies: base, test and local which are needed respectfully during running, testing and developing.
2. Some packages are needed only under Python 2.7.
3. Other packages are needed only under Windows.
4. All packages must be hard-pinned and hashed.

Alternatively, if turned into tasks:

1. Organize dependencies for each environment.
2. Orchestrate installation in different environments.

## Solutions

The first tool we are using is [pip-compile-multi](https://github.com/peterdemin/pip-compile-multi),
which is ~~ironically~~ the project we are using as an example.

It has verbose documentation, so I'll briefly outline how it is applied here.
There are 6 `.in` files in the  `requirements` directory: base.in, test.in, local.in, py27.in, local27.in, testwin.in.
`base`, `test` and `local` are meant to be used under Python 3.
`py27` and `local27` are holding Python 2.7 backports of Python 3 packages and version constraints for projects, which dropped Python 2 support in newer versions.
`testwin` has a single entry: `colorama`, which is `pytest` dependency that is installed only under windows.

First, we are pinning packages to the current versions with the following command:

```
$ pip-compile-multi -n local -n testwin
```

It produces files `base.txt`, `test.txt`, `local.txt` and `testwin.txt` with recursively retrieved hard-pinned package versions.

The second command takes these `.txt` files and produce `.hash` files with attached package hashes:

```
$ pip-compile-multi -n local -n testwin -g local -g testwin -i txt -o hash
```

The same operation must be repeated separately for Python 2.7 packages:

```
$ pip-compile-multi -n py27 -n local27
$ pip-compile-multi -n py27 -n local27 -g py27 -g local27 -i txt -o hash
```

Separation is required because [pip-tools](https://github.com/jazzband/pip-tools)
can't traverse packages that are not required in the current runtime.

To automate this tasks, I'm using the second tool - [tox](https://tox.readthedocs.io/en/latest/).
Here is my configuration:

```
[testenv:upgrade2]
basepython = python2.7
deps = pip-compile-multi
commands =
    pip-compile-multi -n py27 -n local27
    pip-compile-multi -n py27 -n local27 -g py27 -g local27 -i txt -o hash

[testenv:upgrade3]
basepython = python3.6
deps = pip-compile-multi
commands =
    pip-compile-multi -n local -n testwin
    pip-compile-multi -n local -n testwin -g local -g testwin -i txt -o hash
```

To run it, I execute:

```
$ tox -e upgrade3 -e upgrade2
```

To run unit and doc tests locally I have somewhat complex testenv setup:

```
[tox]
envlist = py{27,34,35,36,37}-{linux,windows}

[testenv]
platform = linux: linux
           windows: win32
deps =
    linux: -r{toxinidir}/requirements/test.hash
    windows: -r{toxinidir}/requirements/testwin.hash
    py27: -r{toxinidir}/requirements/py27.hash
commands = python -m pytest --doctest-modules pipcompilemulti.py test_pipcompilemulti.py
```

The setup says to use `test.hash` file under Linux,
`testwin.hash` under Windows and
add `py27.hash` if it is also running under Python 2.7.

AppVeyor runs these tests under Windows; its configuration file defines which Python version to use and what parameters to pass to `tox.ini`:

```
environment:
  matrix:
    - PYTHON: "C:\\Python27"
      PYTHON_VERSION: "2.7.8"
      PYTHON_ARCH: "32"
      TOX_ENV: "py27"

    - PYTHON: "C:\\Python34"
      PYTHON_VERSION: "3.4.1"
      PYTHON_ARCH: "32"
      TOX_ENV: "py34"

    - PYTHON: "C:\\Python35"
      PYTHON_VERSION: "3.5.4"
      PYTHON_ARCH: "32"
      TOX_ENV: "py35"

    - PYTHON: "C:\\Python36"
      PYTHON_VERSION: "3.6.4"
      PYTHON_ARCH: "32"
      TOX_ENV: "py36"

init:
  - "ECHO %PYTHON% %PYTHON_VERSION% %PYTHON_ARCH%"

install:
  - "appveyor/setup_build_env.cmd"
  - "powershell appveyor/install.ps1"

build: false

test_script:
  - "%PYTHON%/Scripts/tox -e %TOX_ENV%-windows"
```

`environment.matrix` defines `TOX_ENV` variable, which is passed to `tox` in `test_script` step.

Travis CI has the following configuration to run tests under Linux:

```
# Config file for automatic testing at travis-ci.org

language: python

python:
  - "3.7-dev"
  - "3.6"
  - "3.5"
  - "3.4"
  - "2.7"
  - "pypy"

# command to install dependencies
install:
  - ./install_test_deps.sh
  - pip install -e .

# command to run tests using coverage, e.g., python setup.py test
script: python -m pytest --doctest-modules pipcompilemulti.py test_pipcompilemulti.py
```

I stashed dependency installation step into bash script `install_test_deps.sh`:

```
#!/bin/sh

python --version 2>&1 | grep -q 'Python 3'

if [ $? -eq 0 ]
then
    # Python 3
    exec pip install -r requirements/test.hash
else
    # Python 2 or PyPy
    exec pip install -r requirements/test.hash -r requirements/py27.hash
fi
```

I could have reused tox here too with [tox-travis](https://github.com/tox-dev/tox-travis).
Someday, maybe, I will.

## Conclusion

Python is multi-platform language, but it lacks built-in tools for secure management of dependencies versions.
Tools like `pip-compile-multi` and `tox` accompanied by CI services like `Travis-ci` and `AppVeyor` significantly reduce the effort. However, correct configuration takes time and requires skills and persistence.

Described solution can be used as a boilerplate for project setup, or as guidance for building another tool that puts a framework for complex dependency management.
