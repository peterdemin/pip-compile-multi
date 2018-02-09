#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "1.1.9"


with open('README.rst') as fp:
    readme = fp.read()


with open('HISTORY.rst') as fp:
    history = fp.read().replace('.. :changelog:', '')


with open(os.path.join('requirements', 'base.in')) as fp:
    requirements = list(fp)


setup(
    name='pip-compile-multi',
    version=version,
    description="""Compile multiple requirements files to lock dependency versions""",
    long_description=readme + '\n\n' + history,
    author='Peter Demin',
    author_email='peterdemin@gmail.com',
    url='https://github.com/peterdemin/pip-compile-multi',
    include_package_data=True,
    py_modules=['pipcompilemulti'],
    install_requires=requirements,
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'pip-compile-multi = pipcompilemulti:cli',
        ]
    },
)
