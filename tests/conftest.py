"""Pytest configuration."""

import shutil
import pathlib
import os.path
import tempfile
import contextlib

import pytest
from click.testing import CliRunner
from pipcompilemulti.options import OPTIONS


@pytest.fixture()
def runner():
    """Fixture for invoking CLI commands."""
    return CliRunner()


@pytest.fixture(autouse=True)
def wipe_options():
    """Reset global OPTIONS dictionary before every test."""
    OPTIONS.clear()


@pytest.fixture()
def test_data_tmpdir():
    """Copy the requested test data to a temporary directory."""

    with contextlib.ExitStack() as stack:

        def copy(test_data_name):
            source = os.path.join('tests', test_data_name)
            tmp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            os.rmdir(tmp_dir)
            shutil.copytree(source, tmp_dir)
            return pathlib.Path(tmp_dir)

        yield copy
