"""End to end tests for CLI v2"""

import os
import tempfile
import shutil

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v1 import cli
from pipcompilemulti.options import OPTIONS


@pytest.fixture(autouse=True)
def requirements_dir():
    """Create temporary requirements directory for test time."""
    tmp_dir = tempfile.mkdtemp()
    os.rmdir(tmp_dir)
    shutil.copytree('requirements', tmp_dir)
    OPTIONS['base_dir'] = tmp_dir
    yield
    shutil.rmtree(tmp_dir)


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade',
                                     '--upgrade-package=pip-tools'])
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
