"""End to end tests for CLI v2"""

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v1 import cli


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade'])
def test_v1_command_exits_with_zero(command):
    """Run pip-compile-multi on self"""
    runner = CliRunner()
    parameters = ['--only-name', 'local']
    parameters.append(command)
    result = runner.invoke(cli, parameters)
    parameters[:0] = ['--generate-hashes', 'local',
                      '--in-ext', 'txt',
                      '--out-ext', 'hash']
    result = runner.invoke(cli, parameters)
    assert result.exit_code == 0


def test_v1_verify_exits_with_zero():
    """Run pip-compile-multi on self"""
    runner = CliRunner()
    result = runner.invoke(cli, ['verify'])
    assert result.exit_code == 0
