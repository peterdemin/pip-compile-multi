"""Environment discovery tests."""

import os
import sys

import pytest

from pipcompilemulti.discover import discover


@pytest.mark.skipif(sys.platform == "win32", reason="Path normalization is wonky under Windows")
def test_discover_nested():
    """Test references to other dirs are discovered."""
    envs = discover(os.path.join("nested", "*.in"))
    assert envs == [
        {
            "in_path": os.path.join("nested", "up.in"),
            "name": "up",
            "refs": set(),
        },
        {
            "in_path": os.path.join("nested", "subproject", "base.in"),
            "name": "base",
            "refs": {os.path.join("..", "up.in")},
        },
        {
            "in_path": os.path.join("nested", "subproject", "sub.in"),
            "name": "sub",
            "refs": {"base.in"},
        },
        {
            "in_path": os.path.join("nested", "base.in"),
            "name": "base",
            "refs": {os.path.join("subproject", "sub.in")},
        },
        {
            "in_path": os.path.join("nested", "diamond.in"),
            "name": "diamond",
            "refs": {"base.in", os.path.join("subproject", "base.in")},
        },
    ]
