"""Test upgrade feature."""

from pipcompilemulti.features import FEATURES
from pipcompilemulti.options import OPTIONS


def test_upgrade_package_disables_upgrade():
    """Even if --update is passed, --upgrade-package disables it."""
    OPTIONS.update({
        'upgrade': True,
        'upgrade_packages': ['a'],
    })
    assert not FEATURES.upgrade_all.enabled
