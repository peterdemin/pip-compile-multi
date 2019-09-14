"""
Limit ``.in`` files
===================

By default ``pip-compile-multi`` compiles all ``.in`` files in ``requirements`` directory.
To limit compilation to only a subset, use

.. code-block:: text

    -n, --only-name TEXT        Compile only for passed environment names and
                                their references. Can be supplied multiple
                                times.

For example, to compile one file under Python2.7 and another under Python3.6, run:

.. code-block:: text

    $ virtual-env27/bin/pip-compile-multi -n deps27
    Locking requirements/deps27.in to requirements/deps27.txt. References: []
    $ virtual-env36/bin/pip-compile-multi -n deps36
    Locking requirements/deps36.in to requirements/deps36.txt. References: []


.. automodule:: pipcompilemulti.features.forbid_post
"""

from pipcompilemulti.utils import recursive_refs
from .base import BaseFeature, ClickOption


class LimitEnvs(BaseFeature):
    """Limit discovered environments to specified subset."""

    OPTION_NAME = 'include_names'
    CLICK_OPTION = ClickOption(
        long_option='--only-name',
        short_option='-n',
        multiple=True,
        help_text='Compile only for passed environment names and their '
                  'references. Can be supplied multiple times.',
    )

    def __init__(self):
        self._all_envs = None

    @property
    def direct_envs(self):
        """Set of environments included by command line options."""
        return set(self.value or [])

    def on_discover(self, env_confs):
        """Save set of all (recursive) included environments."""
        included_and_refs = self.direct_envs
        if not self.direct_envs:
            # No limit means all envs included:
            self._all_envs = [env['name'] for env in env_confs]
            return
        for name in set(included_and_refs):
            included_and_refs.update(
                recursive_refs(env_confs, name)
            )
        self._all_envs = included_and_refs

    def included(self, env_name):
        """Whether environment is included directly or by reference."""
        return env_name in self._all_envs
