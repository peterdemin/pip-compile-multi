"""
Forbid .postX release
=====================

``pip-compile-multi`` can remove ``.postX`` part of dependencies versions.

.. code-block:: text

    -p, --forbid-post TEXT      Environment name (base, test, etc) that cannot
                                have packages with post-release versions
                                (1.2.3.post777).
                                Can be supplied multiple times.

.. note::

    Be careful with this option since different maintainers treat
    post releases differently.
"""

from .base import BaseFeature, ClickOption


class ForbidPost(BaseFeature):
    """Truncate postXXX from versions for selected packages."""

    OPTION_NAME = 'forbid_post'
    CLICK_OPTION = ClickOption(
        long_option='--forbid-post',
        short_option='-p',
        multiple=True,
        help_text="Environment name (base, test, etc) that cannot have "
                  'packages with post-release versions (1.2.3.post777). '
                  'Can be supplied multiple times.'
    )

    @property
    def enabled_envs(self):
        """Convert to set."""
        return set(self.value or [])

    @staticmethod
    def drop_post(version):
        """Remove .postXXXX postfix from version.

        >>> ForbidPost.drop_post('1.2.3.post123')
        '1.2.3'
        >>> ForbidPost.drop_post('1.2.3')
        '1.2.3'
        """
        post_index = version.find('.post')
        if post_index >= 0:
            return version[:post_index]
        return version

    def post_forbidden(self, env_name):
        """Whether post versions are forbidden for passed environment name."""
        return env_name in self.enabled_envs
