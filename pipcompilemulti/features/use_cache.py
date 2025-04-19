"""
Use Cache
=========

By default ``pip-compile-multi`` executes ``pip-compile`` without ``--rebuild`` flag.
``--rebuild`` flag clears any caches upfront and rebuilds from scratch.
Option ``--no-use-cache`` adds ``--rebuild`` flag.

.. code-block:: text

  --use-cache / --no-use-cache    Use pip-tools cache to speed up compilation
                                  (default true)

In configuration file, use ``use_cache`` option::

    [requirements]
    use_cache = False

.. note::

    But if you run into "magical_" issues,
    try rerunning compilation with ``--no-use-cache``.

.. _magical: https://github.com/jazzband/pip-tools/issues?q=--rebuild
"""

from .base import ClickOption
from .forward import ForwardOption


class UseCache(ForwardOption):
    """Use pip-tools cache, or rebuild from scratch."""

    OPTION_NAME = 'use_cache'
    CLICK_OPTION = ClickOption(
        long_option='--use-cache/--no-use-cache',
        is_flag=True,
        default=True,
        help_text='Use pip-tools cache to speed up compilation (default true)',
    )
    disabled_pin_options = ['--rebuild']
