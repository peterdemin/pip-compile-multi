"""Environment discovery tests."""

from pipcompilemulti.discover import discover


def test_discover_nested():
    """Test references to other dirs are discovered."""
    envs = discover('nested/*.in')
    assert envs == [
        {
            'in_path': 'nested/up.in',
            'name': 'up',
            'refs': set(),
        },
        {
            'in_path': 'nested/subproject/base.in',
            'name': 'base',
            'refs': {'../up.in'},
        },
        {
            'in_path': 'nested/subproject/sub.in',
            'name': 'sub',
            'refs': {'base.in'},
        },
        {
            'in_path': 'nested/base.in',
            'name': 'base',
            'refs': {'subproject/sub.in'},
        },
        {
            'in_path': 'nested/diamond.in',
            'name': 'diamond',
            'refs': {'base.in', 'subproject/base.in'},
        },
    ]
