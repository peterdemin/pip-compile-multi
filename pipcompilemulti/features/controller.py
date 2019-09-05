"""Aggregate all features in a single controller."""

from .use_cache import UseCache
from .file_extensions import InputExtension


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
