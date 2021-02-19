"""Utils tests."""

import sys

import pytest

from pipcompilemulti.utils import recursive_refs


@pytest.mark.skipif(sys.platform == "win32", reason="Pass normalization is wonky under Windows")
def test_recursive_refs():
    """Test sample inputs."""
    result = sorted(recursive_refs([
        {'in_path': 'base.in', 'refs': []},
        {'in_path': 'sub/test.in', 'refs': ['../base.in']},
        {'in_path': 'local.in', 'refs': ['sub/test.in']},
    ], 'local.in'))
    assert result == ['base.in', 'sub/test.in']

    result = sorted(recursive_refs([
        {'in_path': 'base.in', 'refs': []},
        {'in_path': 'sub/test.in', 'refs': ['../base.in']},
        {'in_path': 'local.in', 'refs': ['sub/test.in']},
    ], 'sub/test.in'))
    assert result == ['base.in']
