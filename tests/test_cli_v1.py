"""End to end tests for CLI v1"""

import shutil
import os.path
import tempfile
from pathlib import Path

from click.testing import CliRunner
import pytest
from pipcompilemulti.cli_v1 import cli
from pipcompilemulti.options import OPTIONS
from .utils import temp_dir


@pytest.fixture(autouse=True)
def requirements_dir():
    """Create temporary requirements directory for test time."""
    with temp_dir() as tmp_dir:
        OPTIONS['base_dir'] = tmp_dir
        yield


@pytest.mark.parametrize('command', ['--no-upgrade', '--upgrade',
                                     '--upgrade-package=pip-tools'])
def test_v1_command_exits_with_zero(command):
    """Run pip-compile-multi on self.

    pip-compile-multi --only-name local --generate-hashes local \
            --in-ext txt --out-ext hash --use-cache \
            --autoresolve
    """
    runner = CliRunner()
    parameters = [command, '--autoresolve', '--only-name', 'local', '--use-cache']
    result = runner.invoke(cli, parameters)
    parameters.extend([
        '--generate-hashes', 'local',
        '--in-ext', 'txt',
        '--out-ext', 'hash',
    ])
    result = runner.invoke(cli, parameters)
    assert result.exit_code == 0


def test_v1_verify_exits_with_zero():
    """Run pip-compile-multi on self"""
    runner = CliRunner()
    result = runner.invoke(cli, ['verify'])
    assert result.exit_code == 0


def _load_tree(root):
    return {
        x.relative_to(root).name: x.read_text().replace(str(root), 'ROOT')
        for x in root.glob('**/*.txt')
    }


@pytest.mark.parametrize('name, args', [
    ('upgrade', ['-P', 'markupsafe']),
])
def test_package_upgrade(name, args):
    """Run pip-compile-multi with various upgrade arguments"""
    root = os.path.join('tests', name)
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.rmdir(tmp_dir)
        shutil.copytree(root, tmp_dir)

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [*args, '--directory', tmp_dir],
        )
        assert result.exit_code == 0

        expected_root = Path(root + '-expected')
        actual_root = Path(tmp_dir)
        expected = _load_tree(expected_root)
        actual = _load_tree(actual_root)

        assert actual == expected
