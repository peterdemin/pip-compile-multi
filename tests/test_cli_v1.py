"""End to end tests for CLI v2"""

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v1 import cli


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade', 'verify'])
def test_v1_command_exits_with_zero(command):
    """Run pip-compile-multi on self"""
    runner = CliRunner()
    parameters = [command]
    if command != 'verify':
        parameters.extend(['--only-name', 'local'])
    result = runner.invoke(cli, parameters)
    assert result.exit_code == 0
