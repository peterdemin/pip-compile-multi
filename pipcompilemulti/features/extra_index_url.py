"""
.. _extra_index_url:

Add additional index URL to search
==================================

Pip accepts URLs for additional package indexes through ``--extra-index-url``.
The same option can be passed to ``pip-compile-multi`` during compilation.

This option is similar to `annotate_index`_.
The difference is that the passed URL is not saved in any of the files,
which is helpful if the URL contains private credentials.

.. code-block:: text

    --extra-index-url TEXT          Add additional package index URL to search
                                    for package versions. Can be supplied
                                    multiple times.
"""

from .base import BaseFeature, ClickOption


class ExtraIndexUrl(BaseFeature):
    """Forward extra index URLs to to pip-compile."""

    _OPTION = '--extra-index-url'
    OPTION_NAME = 'extra_index_url'
    CLICK_OPTION = ClickOption(
        long_option=_OPTION,
        multiple=True,
        help_text=(
            'Add additional package index URL to search for package versions. '
            'Can be supplied multiple times.'
        )
    )

    def pin_options(self):
        """Pin command options."""
        if self.value:
            parts = []
            for url in self.value:
                parts.extend([self._OPTION, url])
            return parts
        return []
