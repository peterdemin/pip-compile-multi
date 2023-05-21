"""End to end tests checking conflicts detection"""

import pytest
from click.testing import CliRunner
from pipcompilemulti.cli_v1 import cli


@pytest.mark.parametrize('conflict', ['merge', 'ref'])
def test_conflict_detected(test_data_tmpdir, conflict):
    """Following types of version conflicts are detected:

    1. Two files have different version and referenced from the third file.
    2. File adds new constraint on package from referenced file.
    """

    tmp_dir = test_data_tmpdir('conflicting-in-' + conflict)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ['--directory', str(tmp_dir)],
    )
    assert result.exit_code == 1
    assert 'Please add constraints' in str(result.exception)
