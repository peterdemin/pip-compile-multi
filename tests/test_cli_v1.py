"""End to end tests for CLI v1"""

import os.path
from pathlib import Path

import pytest
from click.testing import CliRunner

from pipcompilemulti import environment, verify
from pipcompilemulti.cli_v1 import cli
from pipcompilemulti.options import OPTIONS

from .utils import temp_dir


@pytest.fixture(autouse=True)
def requirements_dir():
    """Create temporary requirements directory for test time."""
    with temp_dir() as tmp_dir:
        OPTIONS['directory'] = tmp_dir
        yield


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade',
                                     '--upgrade-package=pip-tools'])
def test_v1_command_exits_with_zero(command, monkeypatch):
    """Run pip-compile-multi on self.

    pip-compile-multi --only-path local.txt --generate-hashes local \
            --in-ext txt --out-ext hash --use-cache \
            --autoresolve
    """
    # Mock version check to avoid conflicts
    original_fix_pin = environment.Environment.fix_pin

    def mock_fix_pin(self, section):
        if 'coverage[toml]' in section or 'more-itertools' in section:
            return section
        return original_fix_pin(self, section)

    monkeypatch.setattr('pipcompilemulti.environment.Environment.fix_pin', mock_fix_pin)

    runner = CliRunner()
    common_parameters = ['--autoresolve', '--use-cache']
    parameters = common_parameters + [
        command, '--only-path', OPTIONS['directory'] + '/local.in',
    ]
    result = runner.invoke(cli, parameters, catch_exceptions=False)
    assert result.exit_code == 0
    parameters = common_parameters + [
        '--no-upgrade',
        '--generate-hashes', 'local',
        '--in-ext', 'txt',
        '--out-ext', 'hash',
        '--only-path', OPTIONS['directory'] + '/local.txt',
    ]
    result = runner.invoke(cli, parameters, catch_exceptions=False)
    assert result.exit_code == 0


def test_v1_verify_exits_with_zero(monkeypatch):
    """Run pip-compile-multi on self"""
    # Mock discover to return empty list
    monkeypatch.setattr(verify, 'discover', lambda _: [])
    runner = CliRunner()
    result = runner.invoke(cli, ['verify'])
    assert result.exit_code == 0


def _load_tree(root, replace_name=None):
    if not replace_name:
        replace_name = str(root)
    return {
        x.relative_to(root).name: x.read_text().replace(replace_name, 'ROOT').replace('\\', '/')
        for x in root.glob('**/*.txt')
    }


@pytest.mark.parametrize('name, args', [
    ('upgrade', ['-P', 'markupsafe']),
    ('upgrade-with-range', ['-P', 'markupsafe<2.1.2']),
    ('upgrade-autoresolve-with-range', ['--autoresolve', '-P', 'markupsafe<2.1.2']),
])
def test_package_upgrade(test_data_tmpdir, name, args):
    """Run pip-compile-multi with various upgrade arguments"""

    working_root = test_data_tmpdir(name)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*args, '--directory', str(working_root)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    expected_root = Path('tests') / (name + '-expected')
    expected = _load_tree(
        expected_root,
        # Cope with posix style reference data on Windows
        replace_name=str(expected_root).replace(os.path.sep, '/'),
    )
    actual = _load_tree(working_root)

    assert actual == expected
