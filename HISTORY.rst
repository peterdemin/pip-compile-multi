History
=======

2.4.2 (2021-09-01)
------------------

* Fix ``--autoresolve`` when ``--directory="."``.

2.4.1 (2021-04-02)
------------------

* Add ``--live/--no-live`` option to control when to print debug output.
  Thanks to `John Sandall`_ and `Thomas Grainger`_.
  (Issue `#153`_, PRs `#247`_ and `#251`_).

* Add ``--extra-index-url <url>`` option.
  Thanks to `Erik Jan de Vries`_.
  (PRs `#250`_ and `#252`_).

.. _#153: https://github.com/peterdemin/pip-compile-multi/issues/153
.. _#247: https://github.com/peterdemin/pip-compile-multi/pull/247
.. _#250: https://github.com/peterdemin/pip-compile-multi/pull/250
.. _#251: https://github.com/peterdemin/pip-compile-multi/pull/251
.. _#252: https://github.com/peterdemin/pip-compile-multi/pull/252
.. _John Sandall: https://github.com/john-sandall
.. _Thomas Grainger: https://github.com/graingert
.. _Erik Jan de Vries: https://github.com/erikjandevries

2.4.0 (2021-03-17)
------------------

* Update --index/--no-index to --emit-index-url/--no-emit-index-url
  for compatibility with pip-tools 6.0.
  (Issue `#243`_).

.. _#243: https://github.com/peterdemin/pip-compile-multi/issues/243

2.3.2 (2021-02-18)
------------------

* Fix cross-feature logic for --autoresolve and --upgrade-package.
  (PR `#236`_).

.. _#236: https://github.com/peterdemin/pip-compile-multi/pull/236

2.3.1 (2021-02-16)
------------------

* Fix for a bug introduced in 2.2.2 when running pip-compile-multi
  installed for Python 3, and having ``python`` symlinked to Python 2.
  (Issue `#233`_, PR `#234`_).

.. _#233: https://github.com/peterdemin/pip-compile-multi/issues/233
.. _#234: https://github.com/peterdemin/pip-compile-multi/pull/234

2.3.0 (2021-02-04)
------------------

* Make SHA1 hashes of input files in a more robust way (Issue `#215`_).
  Now it ignores changes to comments, whitespace and order of packages.

.. _#215: https://github.com/peterdemin/pip-compile-multi/issues/215

2.2.2 (2021-01-29)
------------------

* Add support for calling using `python -m pipcompilemulti.cli_v1` notation.


2.2.1 (2021-01-29)
------------------

* Add ``--skip-constraints`` option.
* Fix bootstrapping for autoresolve case with missing output files.


2.2.0 (2020-01-22)
------------------

* Add ``--autoresolve`` option for conflict-free compilations (PR #224).
* Auto-discover requirements in other directories by following references (PR #221).
* Add support for new-style multiline "via" comments from pip-tools (PR #222).


2.1.0 (2020-08-19)
------------------

* Update dependencies.
* Revert relative path normalization, introduced in #167 (thanks to @john-bodley #200).


2.0.0 (2020-05-18)
------------------

* Drop Python 2.7 support. pip-tools 4 no longer works with the latest pip,
  there's no way to continue Python 2.7 support.


1.5.9 (2020-03-23)
------------------

* Remove directory path from "via" annotations (thanks to @HALtheWise #166 #167).


1.5.8 (2019-09-27)
------------------

* Add option ``--annotate-index`` (thanks to @john-bodley #160).

1.5.7 (2019-09-27)
------------------

* Enable accidentially disabled ``--upgrade`` option.

.. _1.5.6:

1.5.6 (2019-09-18)
------------------

* Minor fixes to packaging and documentation.

Warning: this version is broken and won't pass ``--upgrade`` option to ``pip-compile``.
If you have this version installed, you need to manually upgrade it.
For example, using command::

    pip-compile-multi --upgrade-package pip-compile-multi

Like in this `PR <https://github.com/mozilla-releng/shipit/pull/1>`_.

1.5.4 (2019-09-16)
------------------

* Fixed MANIFEST to include features directory

Warning: this version is broken and won't pass ``--upgrade`` option to ``pip-compile``.
See notes for 1.5.6_ for details.

1.5.3 (2019-09-14)
------------------

* Refactored features to separate modules.
* Allow passing verify options after verify command.
* Trim irrelevant entries from the traceback.

Warning: this version is broken and won't install ``features`` directory.
See notes for 1.5.6_ for details.

1.5.2 (2019-09-12)
------------------

* Added option ``--allow-unsafe``. (thanks to @mozbhearsum #157).

1.5.1 (2019-08-08)
------------------

* Added option ``--use-cache``. (thanks to @kolotev #149).


1.5.0 (2019-08-06)
------------------

* Changed short option for ``--forbid-post`` from ``-P`` to ``-p``
  (as it conflicted with ``-P`` for ``--upgrade-package`` #147).


1.3.1 (2019-02-19)
------------------

* Re-removed workaround for future[s] packages in Python3

1.3.0 (2018-12-27)
------------------

* Introduced CLI v2 (disabled by default)


1.2.2 (2018-11-20)
------------------

* Removed workaround for future[s] packages in Python3 (no longer needed)

1.2.1 (2018-04-16)
-------------------

* Fixed Restructured text formatting (thanks to @yigor)
* Updated test dependencies (and hashes)

1.2.0 (2018-04-03)
-------------------

* Added --forbid-post option

1.1.12 (2018-02-23)
-------------------

* Added checks for conflicting package versions
* Added support for VCS dependencies
* Added --no-upgrade option

1.1.11 (2018-02-09)
-------------------

* Propagate --only-name option to references
* Fixed extension override options

1.1.10 (2018-02-09)
-------------------

* Added ``--generate-hashes`` option

1.1.9 (2018-02-08)
------------------

* Fixed directory override option
* Added --only-name option

1.1.8 (2018-01-25)
------------------

* Fixed comment justification

1.1.6 (2018-01-19)
------------------

* Added ``pip-compile-multi verify`` command

1.1.5 (2018-01-16)
------------------

* Omit future[s] packages for Python3

1.1.0 (2018-01-12)
------------------

* Added files discovery.

1.0.0 (2018-01-11)
------------------

* First release on PyPI.
