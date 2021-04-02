"""
Limit environments
==================

.. warning::

    This flag is deprecated and will be removed in future releases.
    Use :ref:`limit-in-files` instead.


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
"""

from .base import ClickOption
from .limit_in_paths import LimitInPaths


class LimitEnvs(LimitInPaths):
    """Limit discovered environments to specified subset."""

    OPTION_NAME = 'include_names'
    CLICK_OPTION = ClickOption(
        long_option='--only-name',
        short_option='-n',
        multiple=True,
        help_text='Compile only for passed environment names and their '
                  'references. Can be supplied multiple times.',
    )

    def __init__(self, controller):
        # pylint: disable=super-with-arguments
        self._controller = controller
        super(LimitEnvs, self).__init__()

    @property
    def direct_envs(self):
        """Set of environments included by command line options."""
        return set(
            self._controller.compose_input_file_path(env_name)
            for env_name in self.value or []
        )
