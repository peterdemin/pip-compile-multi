"""
.. _emit_find_links:

Add find-links annotation
=========================

Control addition of ``--find-links`` options to the output files.
Corresponds to ``pip-compile``'s and ``uv pip compile``'s
``--emit-find-links / --no-emit-find-links`` flag.

The URL can be defined in the input file as in this example:

.. code-block:: text

    --find-links=https://download.pytorch.org/whl/torch_stable.html
    torch

By default, ``--find-links`` entries from input files are preserved
in the generated output files.
Pass ``--no-emit-find-links`` to strip them.

.. code-block:: text

    --emit-find-links / --no-emit-find-links
                                    Add find-links to generated files
                                    (default true)

In configuration file, use ``emit_find_links`` option::

    [requirements]
    emit_find_links = False

Note: ``uv pip compile`` strips ``--find-links`` entries by default,
so this flag is forwarded to both ``pip-tools`` and ``uv`` backends
to keep behavior consistent.
"""

from .base import ClickOption
from .forward import ForwardOption


class EmitFindLinks(ForwardOption):
    """Optionally add the find-links entries to the generated files."""

    OPTION_NAME = 'emit_find_links'
    CLICK_OPTION = ClickOption(
        long_option='--emit-find-links/--no-emit-find-links',
        is_flag=True,
        default=True,
        help_text="Add find-links entries to generated files (default true)",
    )
    enabled_pin_options = ['--emit-find-links']
    disabled_pin_options = ['--no-emit-find-links']
