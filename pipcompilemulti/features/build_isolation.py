"""
Build isolation
===============

Allows disabling build isolation through the equivalent ``pip-compile`` flag.
Build isolation is enabled by default.

.. code-block:: text

  --build-isolation / --no-build-isolation
                                  Enable isolation when building a modern
                                  source distribution. Build dependencies
                                  specified by PEP 518 must be already
                                  installed if build isolation is disabled.
"""
from .base import ClickOption
from .forward import ForwardOption


class BuildIsolation(ForwardOption):
    """Proxies build isolation flag to pip-compile"""

    OPTION_NAME = 'build_isolation'
    CLICK_OPTION = ClickOption(
        long_option='--build-isolation/--no-build-isolation',
        is_flag=True,
        default=True,
        help_text=(
            'Enable isolation when building a modern source distribution. '
            'Build dependencies specified by PEP 518 must be already '
            'installed if build isolation is disabled.'
        ),
    )
    disabled_pin_options = ['--no-build-isolation']
