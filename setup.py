#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.1.0"

if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        raise ImportError("Fix: pip install wheel")
    os.system('python setup.py sdist bdist_wheel upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pip-compile-multi',
    version=version,
    description="""Compile multiple requirements files to lock dependency versions""",
    long_description=readme + '\n\n' + history,
    author='Peter Demin',
    author_email='peterdemin@gmail.com',
    url='https://github.com/peterdemin/pip-compile-multi',
    include_package_data=True,
    py_modules=['pip-compile-multi'],
    install_requires=(
        'click',
        'pip-tools',
    ),
    license="MIT",
    zip_safe=False,
    keywords='pip-compile-multi',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'pip-compile-multi = lock:main',
        ]
    },
)
