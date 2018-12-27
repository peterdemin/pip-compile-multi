"""End to end tests for CLI v2"""

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v2 import cli


@pytest.mark.parametrize('command', ['lock', 'upgrade', 'verify'])
def test_command_exits_with_zero(command):
    """Run requirements command on self"""
    runner = CliRunner()
    result = runner.invoke(cli, [command])
    assert result.exit_code == 0
