"""
Backtracking resolver
=====================

Pip has an option to enable `backtracking`_ conflict resolution logic,
which can automatically downgrade some dependencies to meet constraints
from other packages.
See also the `a note on resolvers`_ in ``pip-compile`` project.

.. code-block:: text

    --backtracking / --no-backtracking
                                Enable backtracking resolver. Translates to
                                pip-compile --resolver=backtracking option.

.. _backtracking: https://pip.pypa.io/en/latest/user_guide/\
        #changes-to-the-pip-dependency-resolver-in-20-3-2020
.. _a note on resolvers: https://github.com/jazzband/pip-tools#a-note-on-resolvers
"""

from .base import ClickOption
from .forward import ForwardOption


class Backtracking(ForwardOption):
    """Enable backtracking resolver."""

    OPTION_NAME = 'backtracking'
    CLICK_OPTION = ClickOption(
        long_option='--backtracking/--no-backtracking',
        is_flag=True,
        default=False,
        help_text='Enable backtracking resolver. Translates to '
                  'pip-compile --resolver=backtracking option.'
    )
    enabled_pin_options = ['--resolver=backtracking']
    disabled_pin_options = ['--resolver=legacy']
