"""
Use Cache
=========

By default ``pip-compile-multi`` executes ``pip-compile`` with
``--rebuild`` flag.
This flag clears any caches upfront and rebuilds from scratch.
Such a strategy has proven to be more reliable in `edge cases`_,
but causes significant performance degradation.

Option ``--use-cache`` removes ``--rebuild`` flag from the call
to ``pip-compile``.

.. code-block:: text

    -u, --use-cache             Use pip-tools cache to speed up compilation.

.. note::

    When using ``--use-cache``, ``pip-compile-multi`` can
    run **10 times faster**. But if you run into "magical" issues,
    try to rerun compilation without this flag first.

.. _edge cases: https://github.com/jazzband/pip-tools/issues?q=--rebuild
"""

from .base import ClickOption
from .forward import ForwardOption


class UseCache(ForwardOption):
    """Use pip-tools cache, or rebuild from scratch."""

    OPTION_NAME = 'use_cache'
    CLICK_OPTION = ClickOption(
        long_option='--use-cache',
        short_option='-u',
        is_flag=True,
        default=False,
        help_text='Use pip-tools cache to speed up compilation.',
    )
    disabled_pin_options = ['--rebuild']
