"""Tests for config loading for CLI v2"""
import os
import pathlib
import shutil
import tempfile
from typing import Iterator, List

import pytest

from pipcompilemulti.config import read_config

TESTDATA = pathlib.Path(__file__).parent / 'configs'
ASSETS = {
    path.name: path.read_text(encoding='utf-8')
    for path in TESTDATA.glob('*.*')
    if not path.name.startswith('.')
}


def _write_asset(name: str) -> None:
    pathlib.Path(name).write_text(ASSETS[name], encoding='utf-8')


@pytest.fixture(autouse=True)
def in_temp_dir() -> Iterator[str]:
    """Run each test in a temporary directory"""
    orig_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    try:
        yield temp_dir
    finally:
        os.chdir(orig_dir)
        shutil.rmtree(temp_dir)


def test_load_no_configs() -> None:
    """No config files"""
    got = read_config()
    assert got is None


@pytest.mark.parametrize(
    'asset_name,expected',
    [
        ('setup.cfg', [
            ('requirements:Python 3', {'autoresolve': True}),
        ]),
        ('requirements.ini', [
            ('requirements', {'allow_unsafe': True, 'use_cache': True, 'uv': True}),
        ]),
        ('pyproject.toml', [
            ('one', {'uv': True}),
            ('two', {'generate_hashes': ['file.txt']}),
        ]),
    ]
)
def test_load_single_config(asset_name: str, expected: List) -> None:
    """Load sample config file"""
    _write_asset(asset_name)
    got = read_config()
    assert got == expected


def test_load_two_configs() -> None:
    """Combine setup.cfg and pyproject.toml"""
    _write_asset('setup.cfg')
    _write_asset('pyproject.toml')
    got = read_config()
    assert got == [
        ('one', {'uv': True}),
        ('two', {'generate_hashes': ['file.txt']}),
        ('requirements:Python 3', {'autoresolve': True})
    ]


def test_load_ini_with_empty_pyproject() -> None:
    """Regression test - pyproject without requirements section"""
    _write_asset('setup.cfg')
    pathlib.Path('pyproject.toml').touch()
    got = read_config()
    assert got == [('requirements:Python 3', {'autoresolve': True})]


def test_pyproject_without_section_name() -> None:
    """Regression test - pyproject without requirements section"""
    pathlib.Path('pyproject.toml').write_text(
        "[tool.requirements]\nuv=true\n",
        encoding="utf-8",
    )
    got = read_config()
    assert got == [('config', {'uv': True})]
