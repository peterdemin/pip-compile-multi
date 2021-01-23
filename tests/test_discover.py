"""Environment discovery tests."""

import os
from pipcompilemulti.discover import discover


def test_discover_nested():
    """Test references to other dirs are discovered."""
    envs = discover('nested/*.in')
    assert envs == [
        {
            'in_path': os.path.normpath('nested/up.in'),
            'name': 'up',
            'refs': set(),
        },
        {
            'in_path': os.path.normpath('nested/subproject/base.in'),
            'name': 'base',
            'refs': {os.path.normpath('../up.in')},
        },
        {
            'in_path': os.path.normpath('nested/subproject/sub.in'),
            'name': 'sub',
            'refs': {'base.in'},
        },
        {
            'in_path': os.path.normpath('nested/base.in'),
            'name': 'base',
            'refs': {os.path.normpath('subproject/sub.in')},
        },
        {
            'in_path': os.path.normpath('nested/diamond.in'),
            'name': 'diamond',
            'refs': {'base.in', os.path.normpath('subproject/base.in')},
        },
    ]
