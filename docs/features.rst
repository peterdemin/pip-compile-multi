Features
--------

``pip-compile-multi`` supports many options to customize compilation.
Each option can be specified in requirements configuration file, by replacing dashes with underscores.
For example, `--use-cache` becomes `use_cache`.
Supported configuration files: ``pyproject.toml``, ``requirements.ini``, ``setup.cfg``, ``tox.ini``.

In INI files, use section name starting with ``requirements:``, for example: ``[requirements:Python 3]``

In ``pyproject.toml`` prefix section name with ``tool.pip-compile-multi``, for example: ``[tool.pip-compile-multi.requirements]``.

.. automodule:: pipcompilemulti.features.base_dir

.. automodule:: pipcompilemulti.features.file_extensions

.. automodule:: pipcompilemulti.features.upgrade

.. automodule:: pipcompilemulti.features.use_cache

.. automodule:: pipcompilemulti.features.compatible

.. automodule:: pipcompilemulti.features.add_hashes

.. automodule:: pipcompilemulti.features.unsafe

.. automodule:: pipcompilemulti.features.header

.. automodule:: pipcompilemulti.features.limit_in_paths

.. automodule:: pipcompilemulti.features.annotate_index

.. automodule:: pipcompilemulti.features.extra_index_url

.. automodule:: pipcompilemulti.features.emit_trusted_host

.. automodule:: pipcompilemulti.features.autoresolve

.. automodule:: pipcompilemulti.features.backtracking

.. automodule:: pipcompilemulti.features.skip_constraint_comments

.. automodule:: pipcompilemulti.features.strip_extras

.. automodule:: pipcompilemulti.features.live_output

.. automodule:: pipcompilemulti.features.use_uv

.. automodule:: pipcompilemulti.verify
