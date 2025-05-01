Features
--------

``pip-compile-multi`` supports many options to customize compilation.
Each option can be specified in ``requirements.ini`` file, by replacing dashes with underscores.
Options can also be specified in the ``pyproject.toml`` file by going adding the ``[tool.pip-compile-multi.requirements]``
section and defining the same options there using TOML syntax. If the TOML file is available with that section defined,
it will take precedence over other pip-compile-multi configuration files

For example, `--use-cache` becomes `use_cache`.

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
