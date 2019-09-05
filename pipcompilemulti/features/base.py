"""Common functionality for features activated by command line option."""

from functools import wraps

import click

from ..options import OPTIONS


class ClickOption:
    """Click option parameters."""

    def __init__(self,
                 long_option='',
                 short_option='',
                 is_flag=False,
                 default=False,
                 help_text=''):
        self.long_option = long_option
        self.short_option = short_option
        self.is_flag = is_flag
        self.default = default
        self.help_text = help_text

    def decorator(self):
        """Create click command decorator with this option."""
        return click.option(
            self.long_option,
            self.short_option,
            is_flag=self.is_flag,
            default=self.default,
            help=self.help_text,
        )

    def bind(self, func):
        """Decorate click command with this option."""
        return self.decorator()(func)


class BaseFeature:
    """Base class for features."""

    OPTION_NAME = None
    CLICK_OPTION = None

    def bind(self, func):
        """Bind feature's click option to passed command."""
        @wraps(func)
        def func_with_extra_option(*args, **kwargs):
            """Save option value and call original command without it."""
            self.extract_option(kwargs)
            return func(*args, **kwargs)

        return self.CLICK_OPTION.bind(func_with_extra_option)

    def extract_option(self, kwargs):
        """Pop option value from kwargs and save it in OPTIONS."""
        OPTIONS[self.OPTION_NAME] = kwargs.pop(self.OPTION_NAME)

    @property
    def value(self):
        """Option value."""
        return OPTIONS.get(self.OPTION_NAME, self.CLICK_OPTION.default)
