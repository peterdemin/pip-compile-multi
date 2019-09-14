"""Pytest configuration."""

import pytest
from pipcompilemulti.options import OPTIONS


@pytest.fixture(autouse=True)
def wipe_options():
    """Reset global OPTIONS dictionary before every test."""
    OPTIONS.clear()
