"""Tests for uv flag functionality"""

import pytest
from pipcompilemulti.cli_v2 import cli
from pipcompilemulti.features import FEATURES


@pytest.fixture
def setup_function():
    # Reset use_uv feature before each test
    FEATURES.use_uv.set(False)
    yield
    # Clean up after test
    FEATURES.use_uv.set(False)

def test_upgrade_with_uv_flag(runner, setup_function):
    """Test upgrade command with uv flag"""
    result = runner.invoke(cli, ['upgrade', '--uv'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is True

def test_verify_with_uv_flag(runner, setup_function, monkeypatch):
    """Test verify command with uv flag"""
    # Mock run_configurations to always return [True]
    monkeypatch.setattr('pipcompilemulti.cli_v2.run_configurations', lambda *args, **kwargs: [True])
    result = runner.invoke(cli, ['verify', '-u'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is True

def test_lock_without_uv_flag(runner, setup_function):
    """Test lock command without uv flag"""
    result = runner.invoke(cli, ['lock'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is False

def test_upgrade_without_uv_flag(runner, setup_function):
    """Test upgrade command without uv flag"""
    result = runner.invoke(cli, ['upgrade'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is False

def test_verify_without_uv_flag(runner, setup_function, monkeypatch):
    """Test verify command without uv flag"""
    # Mock run_configurations to always return [True]
    monkeypatch.setattr('pipcompilemulti.cli_v2.run_configurations', lambda *args, **kwargs: [True])
    result = runner.invoke(cli, ['verify'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is False


def test_uv_not_available(runner, setup_function, monkeypatch):
    """Test behavior when UV is not available"""
    # Mock _check_uv_available to return False
    def mock_check_uv():
        return False
    monkeypatch.setattr(
        'pipcompilemulti.environment.Environment._check_uv_available',
        mock_check_uv
    )
    result = runner.invoke(cli, ['upgrade', '--uv'])
    assert result.exit_code != 0
    assert "UV package is not available" in result.output


def test_uv_available(runner, setup_function, monkeypatch):
    """Test behavior when UV is available"""
    # Mock _check_uv_available to return True
    def mock_check_uv():
        return True
    def mock_run_configurations(*args, **kwargs):
        return [True]
    monkeypatch.setattr(
        'pipcompilemulti.environment.Environment._check_uv_available',
        mock_check_uv
    )
    # Mock run_configurations to avoid actual compilation
    monkeypatch.setattr('pipcompilemulti.cli_v2.run_configurations', mock_run_configurations)
    result = runner.invoke(cli, ['upgrade', '--uv'])
    assert result.exit_code == 0
    assert FEATURES.use_uv.get() is True