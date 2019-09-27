"""
Enable indexes
==============

This flag mimics the logic of the ``pip-compile`` ``--index`` and ``--no-index`
flag by opting to add or not add the ``pip`` index to the generated files.

.. code-block:: text

    --index / --no-index     Add index URL to generated files (default false)

Note the default behavior is not to add the index, i.e., ``--no-index`.
"""

from .base import ClickOption
from .forward import ForwardOption


class Index(ForwardOption):
    """Optionally add the index URL to the generated files."""

    OPTION_NAME = "index"
    CLICK_OPTION = ClickOption(
        long_option="--index/--no-index",
        default=False,
        is_flag=True,
        help_text="Add index URL to generated files (default false)",
    )
    enabled_pin_options = ["--index"]
    disabled_pin_options = ["--no-index"]
