"""
Strip extras
============

Instructs ``pip-compile`` to attempt to omit extras in transient dependencies,
while assuring the constraints compatibility.

.. code-block:: text

    --strip-extras          Try avoiding use of extras.
"""
from .base import ClickOption
from .forward import ForwardOption


class StripExtras(ForwardOption):
    """Attempt to drop extras"""

    OPTION_NAME = 'strip_extras'
    CLICK_OPTION = ClickOption(
        long_option='--strip-extras',
        is_flag=True,
        default=False,
        help_text='Try avoiding use of extras.'
    )
    enabled_pin_options = ['--strip-extras']
