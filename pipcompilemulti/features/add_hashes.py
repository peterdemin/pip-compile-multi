"""
Generate hashes
===============

Put package hash after pinned version for additional security.
Format for this option is

.. code-block:: text

  -g, --generate-hashes TEXT  Environment name (base, test, etc.) that needs
                              packages hashes. Can be supplied multiple times.


Example invocation:

.. code-block:: text

    $ pip-compile-multi -g base -g docs

Example output:

.. code-block:: text

    pip-tools==1.11.0 \
        --hash=sha256:50288eb066ce66dbef5401a21530712a93c659fe480c7d8d34e2379300555fa1 \
        --hash=sha256:ba427b68443466c389e3b0b0ef55f537ab39344190ea980dfebb333d0e6a50a3
    first==2.0.1 \
        --hash=sha256:3bb3de3582cb27071cfb514f00ed784dc444b7f96dc21e140de65fe00585c95e \
        --hash=sha256:41d5b64e70507d0c3ca742d68010a76060eea8a3d863e9b5130ab11a4a91aa0e \
        # via pip-tools

``pip`` requires all packages to have hashes if at least one has it.
``pip-compile-multi`` will recursively propagate this option to all
environments that are referencing or referenced by selected environments.
"""  # noqa: E501

from pipcompilemulti.utils import reference_cluster
from .base import BaseFeature, ClickOption


class AddHashes(BaseFeature):
    """Write hashes for pinned packages.

    >>> from pipcompilemulti.options import OPTIONS
    >>> add_hashes = AddHashes()
    >>> OPTIONS[add_hashes.OPTION_NAME] = ['test']
    >>> add_hashes.on_discover([
    ...     {'name': 'base', 'refs': []},
    ...     {'name': 'test', 'refs': ['base']},
    ...     {'name': 'docs', 'refs': []},
    ... ])
    >>> add_hashes.pin_options('base')
    ['--generate-hashes']
    >>> add_hashes.pin_options('docs')
    []
    """

    OPTION_NAME = 'add_hashes'
    CLICK_OPTION = ClickOption(
        long_option='--generate-hashes',
        short_option='-g',
        multiple=True,
        help_text='Environment name (base, test, etc) that needs '
                  'packages hashes. '
                  'Can be supplied multiple times.',

    )

    def __init__(self):
        self._hashed_by_reference = None

    @property
    def enabled_envs(self):
        """Convert list of environment names to a set."""
        return set(self.value or [])

    def on_discover(self, env_confs):
        """Save environment names that need hashing."""
        self._hashed_by_reference = set()
        for name in self.enabled_envs:
            self._hashed_by_reference.update(
                reference_cluster(env_confs, name)
            )

    def _needs_hashes(self, env_name):
        assert self._hashed_by_reference is not None
        return env_name in self._hashed_by_reference

    def pin_options(self, env_name):
        """Return --generate-hashes if env requires it."""
        if self._needs_hashes(env_name):
            return ['--generate-hashes']
        return []
