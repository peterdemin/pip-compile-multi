"""
Live output
===========

Print debug output from pip-compile live.
If the option is disabled (by default) the debug output
is printed only in case of failure.

.. code-block:: text

    --live / --no-live              Print debug output from pip-compile live.
"""
import subprocess

from .base import BaseFeature, ClickOption


class LiveOutput(BaseFeature):
    """Controls whether stdout and stderr should be printed live or at error."""

    OPTION_NAME = 'live'
    CLICK_OPTION = ClickOption(
        long_option='--live/--no-live',
        default=False,
        is_flag=True,
        help_text='Print debug output from pip-compile live.',
    )

    def pipe_arguments(self):
        """Values for stdout and stderr arguments to subprocess.Popen."""
        if self.value:
            return {}
        return {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
