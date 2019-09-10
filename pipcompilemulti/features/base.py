"""Common functionality for features activated by command line option."""

import click

from ..options import OPTIONS


class ClickOption:
    """Click option parameters."""

    def __init__(self,
                 long_option='',
                 short_option='',
                 is_flag=False,
                 default=None,
                 multiple=False,
                 help_text=''):
        self.long_option = long_option
        self.short_option = short_option
        self.is_flag = is_flag
        self.default = default
        self.multiple = multiple
        self.help_text = help_text

    def decorate(self, command):
        """Decorate click command with this option."""
        return self.decorator()(command)

    def decorator(self):
        """Create click command decorator with this option."""
        args = [self.long_option]
        kwargs = dict(
            is_flag=self.is_flag,
            multiple=self.multiple,
            help=self.help_text,
        )
        if self.short_option:
            args.append(self.short_option)
        if self.default:
            kwargs.update(default=self.default)
        return click.option(*args, **kwargs)

    @property
    def argument_name(self):
        """Generate command argument name from long option.

        >>> ClickOption("--param-name").argument_name
        'param_name'
        >>> ClickOption("--param-name/--no-param-name").argument_name
        'param_name'
        """
        return self.long_option.lstrip('--').split('/', 1)[0].replace('-', '_')


class BaseFeature:
    """Base class for features."""

    OPTION_NAME = None
    CLICK_OPTION = None

    def bind(self, command):
        """Bind feature's click option to passed command."""
        return self.CLICK_OPTION.decorate(command)

    def extract_option(self, kwargs):
        """Pop option value from kwargs and save it in OPTIONS.

        If option was saved before and new value is the same as default,
        then keep previous value.
        This allows passing options both before and after ``verify`` command.
        """
        new_value = kwargs.pop(self.CLICK_OPTION.argument_name)
        if self.OPTION_NAME in OPTIONS and new_value == self.CLICK_OPTION.default:
            # Do not overwrite with default if already set.
            return
        OPTIONS[self.OPTION_NAME] = new_value

    @property
    def value(self):
        """Option value."""
        return OPTIONS.get(self.OPTION_NAME, self.CLICK_OPTION.default)
