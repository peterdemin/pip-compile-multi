"""Package configuration"""

import os
from setuptools import setup, find_packages


VERSION = "2.0.0"


README = """
pip-compile-multi
=================

Compile multiple requirements files to lock dependency versions.

Install
-------

.. code-block:: shell

    pip install pip-compile-multi

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


with open('HISTORY.rst') as fp:
    HISTORY = fp.read().replace('.. :changelog:', '')


with open(os.path.join('requirements', 'base.in')) as fp:
    REQUIREMENTS = list(fp)


CONSOLE_SCRIPTS = [
    'pip-compile-multi = pipcompilemulti.cli_v1:cli',
]
if os.environ.get('PCM_ALPHA') == 'ON':
    CONSOLE_SCRIPTS.append(
        'requirements = pipcompilemulti.cli_v2:cli'
    )


setup(
    name='pip-compile-multi',
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
    python_requires='~=3.6',
    license="MIT",
    zip_safe=False,
    keywords='pip-compile-multi',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
    },
    setup_requires=['setuptools', 'wheel'],
)
