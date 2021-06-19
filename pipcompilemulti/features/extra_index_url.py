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


.. warning::

    Using ``--extra-index-url`` option to search for packages that are not in
    the main repository (such as private packages) is unsafe, per a security vulnerability
    called `dependency confusion`_: an attacker can claim the package on
    the public repository in a way that will ensure it gets chosen over the private package.

    Use the ``--index-url`` option in pip’s configuration file or command line
    to specify the feed, overriding the default.
    Avoid the ``--extra-index-url`` option, which is additive and may lead
    to having multiple indexes.

    See `pip documentation`_ for details.

.. _pip documentation: https://pip.pypa.io/en/stable/cli/pip_install/#examples
.. _dependency confusion: https://azure.microsoft.com/en-us/resources/\
        3-ways-to-mitigate-risk-using-private-package-feeds/
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
