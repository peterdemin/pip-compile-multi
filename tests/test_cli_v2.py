"""End to end tests for CLI v2"""

from functools import partial

try:
    from unittest import mock
except ImportError:
    import mock
from click.testing import CliRunner

import pytest

from pipcompilemulti.cli_v2 import cli, read_config
from .utils import temp_dir


@pytest.fixture(autouse=True)
def requirements_dir():
    """Create temporary requirements directory for test time."""
    with temp_dir() as tmp_dir:
        patch = partial(patched_config, tmp_dir)
        with mock.patch('pipcompilemulti.cli_v2.read_config', patch):
            yield


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
