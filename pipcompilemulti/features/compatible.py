"""
Compatible Releases
===================

`PEP-440`_ describes compatible release operator ``~=``.
Sometimes it's useful to have some of the dependencies
pinned using this operator.
For example, rapidly changing internal libraries.
The format for this option is

.. code-block:: text

    -c, --compatible TEXT

where TEXT is a `glob`_ pattern for library name.
This option can be supplied multiple times.

.. _glob: https://en.wikipedia.org/wiki/Glob_(programming)
.. _PEP-440: https://www.python.org/dev/peps/pep-0440/#compatible-release
"""

from fnmatch import fnmatch

from .base import BaseFeature, ClickOption


class Compatible(BaseFeature):
    """Use ~= for selected packages."""

    OPTION_NAME = 'compatible_patterns'
    CLICK_OPTION = ClickOption(
        long_option='--compatible',
        short_option='-c',
        multiple=True,
        help_text='Glob expression for packages with compatible (~=) '
                  'version constraint. Can be supplied multiple times.'
    )

    @property
    def patterns(self):
        """Use empty list as the default."""
        return self.value or []

    def constraint(self, package_name):
        """Return ``~=`` if package_name matches patterns, ``==`` otherwise.

        >>> from pipcompilemulti.options import OPTIONS
        >>> feature = Compatible()
        >>> OPTIONS[feature.OPTION_NAME] = ['xxx']
        >>> feature.constraint('package')
        '=='
        >>> feature.constraint('xxx')
        '~='
        """
        return '~=' if self.is_matched(package_name) else '=='

    def is_matched(self, package_name):
        """Whether package name matches one of configured glob patterns."""
        package = package_name.lower()
        for pattern in self.patterns:
            if fnmatch(package, pattern):
                return True
        return False
