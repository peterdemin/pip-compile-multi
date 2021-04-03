"""
.. _annotate_index:

Add index URL annotation
========================

This flag provides the ability to annotate the index URL mimicking the logic of
the ``pip-compile`` ``--emit-index-url`` and ``--no-emit-index-url`` flag
by opting to add or not add the ``pip`` index to the generated files.

The URL can be set in the input file as in this example:

.. code-block:: text

    --index-url=https://pypi.tuna.tsinghua.edu.cn/simple/
    six
    click

This option is similar to `extra_index_url`_.
The difference is that URL is saved in the output files,
which means that it doesn't need to be configured in every environment.

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
    enabled_pin_options = ["--emit-index-url"]
    disabled_pin_options = ["--no-emit-index-url"]
