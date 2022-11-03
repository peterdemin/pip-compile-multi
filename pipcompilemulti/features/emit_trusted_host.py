"""
.. _emit_trusted_host:

Add trusted host annotation
===========================

Control addition of trusted hosts for index URLs to generated files.
Trusted hosts can be defined in ``pip.conf`` file, input requirements file,
or through an argument to ``pip`` command.
Trusted hosts can have invalid HTTPS certificate, or use unencrypted HTTP protocol.

By default, trusted hosts are saved in the generated files.
Pass ``--no-emit-trusted-host`` to remove it.

If no trusted hosts are defined, this flag doesn't have any effect.

.. code-block:: text

    --emit-trusted-host / --no-emit-trusted-host
                                    Add trusted host to generated files
                                    (default true)

See also: `annotate_index`_ and `extra_index_url`_ options.

See pip-tools issue `#382`_ for more details.

.. _#382: https://github.com/jazzband/pip-tools/issues/382
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
