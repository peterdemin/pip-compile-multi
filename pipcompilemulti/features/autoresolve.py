"""
.. _autoresolve:

Autoresolve cross-file conflicts
================================

Compile requirements file, that references all other files first,
and than use it as a constraint.

.. code-block:: text

    --autoresolve/--no-autoresolve Automatically resolve
                                   cross-file conflicts.

This strategy allows to resolve cross-file conflicts of two types:

1. Files FOO and BAR both have dependency PKG, but compile it to different versions.
2. FOO has PKG resolved to version 3. BAR references FOO, but also
   has another dependency, that constraints PKG to version 2.

By compiling all-including file (aka *sink*), that references both FOO and BAR first,
pip-compile-multi generates conflict-free set of versions.

After that, this compiled file is passed as a constraint for compiling
all requirements files.

As the last step, the *sink* file is compiled again preserving reference files
and skipping duplicate packages.

.. note::

    This feature works only if your project has a single requirements file,
    that references (directly or indirectly) all other files.
"""

from pipcompilemulti.utils import recursive_refs
from .base import BaseFeature, ClickOption


class Autoresolve(BaseFeature):
    """Detect sink file and use it unless the feature is explicitly disabled."""

    OPTION_NAME = 'autoresolve'
    CLICK_OPTION = ClickOption(
        long_option='--autoresolve/--no-autoresolve',
        is_flag=True,
        default=False,
        help_text='Automatically resolve cross-file conflicts.',
    )

    def __init__(self):
        self._sink_path = None

    @property
    def enabled(self):
        """Whether feature was explicitly disabled or not."""
        return self.value

    def on_discover(self, env_confs):
        """Save set of all (recursive) included environments."""
        self._sink_path = self._find_sink(env_confs)

    def sink_path(self):
        """Return sink path if it's enabled. Otherwise None"""
        return self._sink_path if self.enabled else None

    @staticmethod
    def _find_sink(envs):
        """Try to find requirements sink.

        Sink is a requirements file that references all other
        requirement files.

        If no sink exists, return None.

        >>> Autoresolve._find_sink([
        ...  {'in_path': 'base', 'refs': set()},
        ...  {'in_path': 'test', 'refs': {'base'}},
        ...  {'in_path': 'local', 'refs': {'test', 'base'}},
        ... ])
        'local'
        >>> Autoresolve._find_sink([
        ...  {'in_path': 'base', 'refs': set()},
        ...  {'in_path': 'test', 'refs': {'base'}},
        ...  {'in_path': 'doc', 'refs': set()},
        ... ])
        >>> Autoresolve._find_sink([
        ...  {'in_path': 'base', 'refs': set()},
        ...  {'in_path': 'foo', 'refs': {'base'}},
        ...  {'in_path': 'bar', 'refs': {'base'}},
        ...  {'in_path': 'all', 'refs': {'foo', 'bar'}},
        ... ])
        'all'
        """
        all_envs = {env['in_path'] for env in envs}
        for env in envs:
            included_envs = set(recursive_refs(envs, env['in_path'])) | {env['in_path']}
            if all_envs == included_envs:
                return env['in_path']
        return None
