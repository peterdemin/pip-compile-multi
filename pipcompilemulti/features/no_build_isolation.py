from .base import ClickOption
from .forward import ForwardOption


class NoBuildIsolation(ForwardOption):
    """
    Enable isolation when building a modern source distribution.
    Build dependencies specified by PEP 518 must be already installed if build isolation is disabled.
    """

    OPTION_NAME = 'no_build_isolation'
    CLICK_OPTION = ClickOption(
        long_option='--no-build-isolation',
        is_flag=True,
        default=False,
        help_text=(
            'Enable isolation when building a modern source distribution. '
            'Build dependencies specified by PEP 518 must be already installed if build isolation is disabled.'
        ),
    )
    enabled_pin_options = ['--no-build-isolation']
