"""Common functionality for features activated by command line option."""

from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast

import click

from ..options import OPTIONS
from ..types import OptionValue

Command = TypeVar("Command", bound=Callable[..., Any])
Value = TypeVar("Value", bound=OptionValue)


class ClickOption:
    """Click option parameters."""

    def __init__(
        self,
        long_option: str = "",
        short_option: str = "",
        *,
        is_flag: bool = False,
        default: OptionValue = None,
        multiple: bool = False,
        help_text: str = "",
    ) -> None:
        self.long_option = long_option
        self.short_option = short_option
        self.is_flag = is_flag
        self.default = default
        self.multiple = multiple
        self.help_text = help_text

    def decorate(self, command: Command) -> Command:
        """Decorate click command with this option."""
        return self.decorator()(command)

    def decorator(self) -> Callable[[Command], Command]:
        """Create click command decorator with this option."""
        args = [self.long_option]
        kwargs: dict[str, Any] = {
            "is_flag": self.is_flag,
            "multiple": self.multiple,
            "help": self.help_text,
        }
        if self.short_option:
            args.append(self.short_option)
        if self.default:
            kwargs.update(default=self.default)
        return click.option(*args, **kwargs)

    @property
    def argument_name(self) -> str:
        """Generate command argument name from long option.

        >>> ClickOption("--param-name").argument_name
        'param_name'
        >>> ClickOption("--param-name/--no-param-name").argument_name
        'param_name'
        """
        return self.long_option.lstrip("-").split("/", 1)[0].replace("-", "_")


class BaseFeature(Generic[Value]):
    """Base class for features."""

    OPTION_NAME: str | None = None
    CLICK_OPTION: ClickOption | None = None

    def bind(self, command: Command) -> Command:
        """Bind feature's click option to passed command."""
        assert self.CLICK_OPTION is not None
        return self.CLICK_OPTION.decorate(command)

    def extract_option(self, kwargs: dict[str, OptionValue]) -> None:
        """Pop option value from kwargs and save it in OPTIONS.

        If option was saved before and new value is the same as default,
        then keep previous value.
        This allows passing options both before and after ``verify`` command.
        """
        assert self.CLICK_OPTION is not None and self.OPTION_NAME is not None
        new_value = kwargs.pop(self.CLICK_OPTION.argument_name)
        if self.OPTION_NAME in OPTIONS and new_value == self.CLICK_OPTION.default:
            # Do not overwrite with default if already set.
            return
        OPTIONS[self.OPTION_NAME] = new_value

    @property
    def value(self) -> Value:
        """Option value."""
        assert self.CLICK_OPTION is not None and self.OPTION_NAME is not None
        # Each concrete feature declares the value type for its option key.
        return cast(Value, OPTIONS.get(self.OPTION_NAME, self.CLICK_OPTION.default))

    @value.setter
    def value(self, new_value: Value) -> None:
        assert self.OPTION_NAME is not None
        OPTIONS[self.OPTION_NAME] = new_value
