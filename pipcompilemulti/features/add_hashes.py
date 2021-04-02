"""
Generate hashes
===============

Put package hash after pinned version for additional security.
Format for this option is

.. code-block:: text

  -g, --generate-hashes TEXT  Input file name (base.in, requirements/test.in, etc)
                              that needs packages hashes.
                              Can be supplied multiple times.
                              For backwards compatibility can be short
                              environment name (base, test, etc.)

Example invocation:

.. code-block:: shell

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
import os

from pipcompilemulti.utils import reference_cluster
from .base import BaseFeature, ClickOption


class AddHashes(BaseFeature):
    """Write hashes for pinned packages."""

    OPTION_NAME = 'add_hashes'
    CLICK_OPTION = ClickOption(
        long_option='--generate-hashes',
        short_option='-g',
        multiple=True,
        help_text='Input file name (base.in, requirements/test.in, etc) '
                  'that needs packages hashes. '
                  'Can be supplied multiple times.',

    )

    def __init__(self, controller):
        self._controller = controller
        self._hashed_by_reference = None

    @property
    def enabled_in_paths(self):
        """Convert list of .in paths to a set.

        For backwards compatibility, check if passed value is env name
        and convert it to in_path.
        """
        names_or_paths = self.value or []
        in_paths = set()
        for name_or_path in names_or_paths:
            in_path = self._controller.compose_input_file_path(name_or_path)
            if os.path.exists(in_path):
                in_paths.add(in_path)
            else:
                in_paths.add(name_or_path)
        return in_paths

    def on_discover(self, env_confs):
        """Save environment names that need hashing."""
        self._hashed_by_reference = set()
        for in_path in self.enabled_in_paths:
            self._hashed_by_reference.update(
                reference_cluster(env_confs, in_path)
            )

    def _needs_hashes(self, in_path):
        assert self._hashed_by_reference is not None
        return in_path in self._hashed_by_reference

    def pin_options(self, in_path):
        """Return --generate-hashes if env requires it."""
        if self._needs_hashes(in_path):
            return ['--generate-hashes']
        return []
