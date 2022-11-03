"""
Add trusted host annotation
========================

This flag provides the ability to annotate the trusted host mimicking the logic of
the ``pip-compile`` ``--emit-trusted-host`` and ``--no-emit-trusted-host`` flag
by opting to add or not add the ``pip`` trusted host to the generated files.

.. code-block:: text

    --emit-trusted-host / --no-emit-trusted-host    Add trusted host to generated files (default true)

Note the default behavior is to add the trusted host, i.e., ``--emit-trusted-host``.
"""

from .base import ClickOption
from .forward import ForwardOption


class EmitTrustedHost(ForwardOption):
    """Optionally add the trusted host to the generated files."""

    OPTION_NAME = 'emit_trusted_host'
    CLICK_OPTION = ClickOption(
        long_option='--emit-trusted-host/--no-emit-trusted-host',
        is_flag=True,
        default=True,
        help_text="Add trusted host option to generated file"
    )
    enabled_pin_options = ['--emit-trusted-host']
    disabled_pin_options = ['--no-emit-trusted-host']
