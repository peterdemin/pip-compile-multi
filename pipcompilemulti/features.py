"""Features incapsulation."""

from functools import wraps

import click

from .options import OPTIONS


class FeaturesController:
    """Gateway to a list of features."""

    def __init__(self):
        self.use_cache = UseCache()
        self.input_extension = InputExtension()
        self._features = [
            self.use_cache,
            self.input_extension,
        ]

    def bind(self, command):
        """Bind all features to click command."""
        for feature in self._features:
            command = feature.bind(command)
        return command

    def pin_options(self):
        """Return list of options to pin command."""
        return self.use_cache.pin_options()

    def compose_input_file_name(self, env_name):
        """Return input file name by environment name."""
        return self.input_extension.compose_input_file_name(env_name)


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
            self.extract_option(kwargs)
            return func(*args, **kwargs)

        return self.CLICK_OPTION.bind(func_with_extra_option)

    def extract_option(self, kwargs):
        """Pop option value from kwargs and save it in OPTIONS."""
        OPTIONS[self.OPTION_NAME] = kwargs.pop(self.OPTION_NAME)


class UseCache(BaseFeature):
    """
    Use Cache
    =========

    By default ``pip-compile-multi`` executes ``pip-compile`` with ``--rebuild`` flag.
    This flag clears any caches upfront and rebuilds from scratch.
    Such a strategy has proven to be more reliable in `edge cases`_,
    but causes significant performance degradation.

    Option ``--use-cache`` removes ``--rebuild`` flag from the call to ``pip-compile``.

    .. code-block:: text

        -u, --use-cache             Use pip-tools cache to speed up compilation.

    .. note::

        When using ``--use-cache``, ``pip-compile-multi`` can run **10 times faster**.
        But if you run into "magical" issues, try to rerun compilation without this flag first.

    .. _edge cases: https://github.com/jazzband/pip-tools/issues?q=--rebuild
    """

    OPTION_NAME = 'use_cache'
    CLICK_OPTION = ClickOption(
        long_option='--use-cache',
        short_option='-u',
        is_flag=True,
        default=False,
        help_text='Use pip-tools cache to speed up compilation.',
    )

    @property
    def enabled(self):
        """Is this feature enabled."""
        return OPTIONS[self.OPTION_NAME]

    def pin_options(self):
        """Return command-line options for pin command.

        >>> UseCache().pin_options()
        ['--rebuild']
        """
        if self.enabled:
            return []
        return ['--rebuild']


class InputExtension(BaseFeature):
    """
    Requirements Files Extensions
    =============================

    By default ``pip-compile-multi`` compiles ``*.txt`` from ``*.in`` files.
    While this is a common naming pattern, each project can use it's own:

    .. code-block:: text

        -i, --in-ext TEXT      File extension of input files
        -o, --out-ext TEXT     File extension of output files
    """

    OPTION_NAME = 'in_ext'
    CLICK_OPTION = ClickOption(
        long_option='--in-ext',
        short_option='-i',
        default="in",
        is_flag=False,
        help_text='File extension of input files.',
    )

    @property
    def value(self):
        """Extension string."""
        return OPTIONS[self.OPTION_NAME]

    def compose_input_file_name(self, env_name):
        """Compose file name given environment name.

        >>> InputExtension().compose_input_file_name('base')
        'base.in'
        """
        return '{0}.{1}'.format(env_name, self.value)


FEATURES = FeaturesController()
