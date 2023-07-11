from .base import ClickOption
from .forward import ForwardOption


class StripExtras(ForwardOption):
    """Use pip-tools cache, or rebuild from scratch."""

    OPTION_NAME = 'strip_extras'
    CLICK_OPTION = ClickOption(
        long_option='--strip-extras',
        is_flag=True,
        default=False,
        help_text='Assure output file is constraints '
                  'compatible, avoiding use of extras.'
    )
    enabled_pin_options = ['--strip-extras']
