"""
.. _limit-in-files:

Limit input files
=================

By default ``pip-compile-multi`` compiles all ``.in`` files in ``requirements`` directory.
To limit compilation to only a subset, use

.. code-block:: text

    -t, --only-path TEXT        Compile only for passed input file paths and
                                their references.
                                Can be supplied multiple times.

For example, to compile one file under Python2.7 and another under Python3.6, run:

.. code-block:: text

    $ virtual-env27/bin/pip-compile-multi -t requirements/deps27.in
    Locking requirements/deps27.in to requirements/deps27.txt. References: []
    $ virtual-env36/bin/pip-compile-multi -t requirements/deps36.in
    Locking requirements/deps36.in to requirements/deps36.txt. References: []
"""

from pipcompilemulti.utils import recursive_refs
from .base import BaseFeature, ClickOption


class LimitInPaths(BaseFeature):
    """Limit discovered input files to specified subset.

    >>> from pipcompilemulti.options import OPTIONS
    >>> feature = LimitInPaths()
    >>> OPTIONS[feature.OPTION_NAME] = ['test.in']
    >>> feature.on_discover([
    ...     {'in_path': 'base.in', 'refs': []},
    ...     {'in_path': 'test.in', 'refs': ['base.in']},
    ...     {'in_path': 'docs.in', 'refs': []},
    ... ])
    >>> feature.included('base.in')
    True
    >>> feature.included('test.in')
    True
    >>> feature.included('docs.in')
    False
    """

    OPTION_NAME = 'include_in_paths'
    CLICK_OPTION = ClickOption(
        long_option='--only-path',
        short_option='-t',
        multiple=True,
        help_text='Compile only for passed input paths and their '
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
        if not self.direct_envs:
            # No limit means all envs included:
            self._all_envs = [env['in_path'] for env in env_confs]
            return
        transitive_refs = {
            ref
            for in_path in self.direct_envs
            for ref in recursive_refs(env_confs, in_path)
        }
        self._all_envs = self.direct_envs | transitive_refs

    def included(self, in_path):
        """Whether environment is included directly or by reference."""
        return in_path in self._all_envs
