"""Package configuration"""

import os
from setuptools import setup, find_packages


VERSION = "3.2.2"


README = """
pip-compile-multi
=================

Compile multiple requirements files to lock dependency versions.

Install
-------

.. code-block:: shell

    pip install pip_compile_multi

Run
----

.. code-block:: shell

    pip-compile-multi


Links
-----

* Documentation: https://pip-compile-multi.readthedocs.io/en/latest/
* Releases: https://pypi.python.org/pypi/pip-compile-multi
* Code: https://github.com/peterdemin/pip-compile-multi
* Issue tracker: https://github.com/peterdemin/pip-compile-multi/issues

"""


with open('HISTORY.rst', encoding='utf-8') as fp:
    HISTORY = fp.read().replace('.. :changelog:', '')


with open(os.path.join('requirements', 'base.in'), encoding='utf-8') as fp:
    REQUIREMENTS = list(fp)


CONSOLE_SCRIPTS = [
    'pip-compile-multi = pipcompilemulti.cli_v1:cli',
    'requirements = pipcompilemulti.cli_v2:cli',
]


setup(
    name='pip_compile_multi',
    version=VERSION,
    description="Compile multiple requirements files "
                "to lock dependency versions",
    long_description=README + '\n\n' + HISTORY,
    author='Peter Demin',
    author_email='peterdemin@gmail.com',
    url='https://github.com/peterdemin/pip-compile-multi',
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIREMENTS,
    python_requires='~=3.9',
    license="MIT",
    zip_safe=False,
    keywords='pip-compile-multi',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Console',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
    },
    setup_requires=['setuptools', 'wheel'],
)
