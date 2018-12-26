"""End to end tests for CLI v2"""

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v1 import cli


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade', 'verify'])
def test_v1_command_exits_with_zero(command):
    """Run pip-compile-multi on self"""
    runner = CliRunner()
    result = runner.invoke(cli, [command])
    assert result.exit_code == 0
