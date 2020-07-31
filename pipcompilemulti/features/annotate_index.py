"""
Add index URL annotation
========================

This flag provides the ability to annotate the index URL mimicking the logic of
the ``pip-compile`` ``--index`` and ``--no-index`` flag by opting to add or not
add the ``pip`` index to the generated files.

.. code-block:: text

    --annotate-index / --no-annotate-index    Add index URL to generated files (default false)

Note the default behavior is not to add the index, i.e., ``--no-annotate-index``.
"""

from .base import ClickOption
from .forward import ForwardOption


class AnnotateIndex(ForwardOption):
    """Optionally annotate the index URL to the generated files."""

    OPTION_NAME = "annotate_index"
    CLICK_OPTION = ClickOption(
        long_option="--annotate-index/--no-annotate-index",
        default=False,
        is_flag=True,
        help_text="Add the index URL to generated files (default false).",
    )
    enabled_pin_options = ["--index"]
    disabled_pin_options = ["--no-index"]
