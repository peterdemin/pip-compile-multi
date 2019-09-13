"""End to end tests for CLI v2"""

import os
import tempfile
import shutil
from functools import partial

try:
    from unittest import mock
except ImportError:
    import mock
from click.testing import CliRunner

import pytest

from pipcompilemulti.cli_v2 import cli, read_config


@pytest.fixture(autouse=True)
def requirements_dir():
    """Create temporary requirements directory for test time."""
    tmp_dir = tempfile.mkdtemp()
    os.rmdir(tmp_dir)
    shutil.copytree('requirements', tmp_dir)
    with mock.patch('pipcompilemulti.cli_v2.read_config', partial(patched_config, tmp_dir)):
        yield
    shutil.rmtree(tmp_dir)


@pytest.mark.parametrize('command', ['lock', 'upgrade', 'verify'])
def test_command_exits_with_zero(command):
    """Run requirements command on self"""
    # pylint: disable=redefined-outer-name
    runner = CliRunner()
    result = runner.invoke(cli, [command])
    assert result.exit_code == 0


def patched_config(base_dir):
    """Override base_dir in each section of config."""
    config_sections = read_config()
    for _, section in config_sections:
        section['base_dir'] = base_dir
    return config_sections
