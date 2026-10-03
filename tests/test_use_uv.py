"""Tests for locating uv."""

# pylint: disable=missing-function-docstring

import sys

import pytest

from pipcompilemulti.features import use_uv
from pipcompilemulti.features.controller import FeaturesController
from pipcompilemulti.options import OPTIONS


@pytest.fixture(name="installed")
def installed_fixture(monkeypatch):
    """Control whether uv is importable and what is on PATH."""

    def install(package, path):
        monkeypatch.setattr(
            use_uv.importlib.util, "find_spec", lambda name: object() if package else None
        )
        monkeypatch.setattr(use_uv.shutil, "which", lambda name: path)

    return install


def test_prefers_the_uv_package_next_to_pip_compile_multi(installed):
    installed(package=True, path="/opt/homebrew/bin/uv")
    assert use_uv.UseUV.executable() == [sys.executable, "-m", "uv"]


def test_falls_back_to_uv_on_path(installed):
    installed(package=False, path="/opt/homebrew/bin/uv")
    assert use_uv.UseUV.executable() == ["/opt/homebrew/bin/uv"]


def test_pin_command_runs_uv_from_path(installed):
    installed(package=False, path="/opt/homebrew/bin/uv")
    OPTIONS["uv"] = True
    assert FeaturesController().pin_command()[:3] == ["/opt/homebrew/bin/uv", "pip", "compile"]


def test_pin_command_fails_when_uv_is_not_installed(installed):
    installed(package=False, path=None)
    OPTIONS["uv"] = True
    with pytest.raises(RuntimeError, match="uv is not installed"):
        FeaturesController().pin_command()


def test_pip_tools_runs_under_the_current_interpreter():
    assert FeaturesController().pin_command()[:3] == [sys.executable, "-m", "piptools"]
