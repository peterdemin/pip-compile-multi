"""Base feature for forwarding pip-tools options."""

from .base import BaseFeature


class ForwardOption(BaseFeature):
    """Forward command line option to pip-tools."""

    #: Pin command options when feature is enabled.
    enabled_pin_options = []
    #: Pin command options when feature is disabled.
    disabled_pin_options = []

    @property
    def enabled(self):
        """Is feature enabled."""
        return self.value

    def pin_options(self):
        """Pin command options."""
        if self.enabled:
            return self.enabled_pin_options
        return self.disabled_pin_options
