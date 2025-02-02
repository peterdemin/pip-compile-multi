import pytest
from pipcompilemulti.cli_v2 import cli
from pipcompilemulti.options import OPTIONS

@pytest.fixture
def setup_function():
    # Reset OPTIONS before each test
    OPTIONS.clear()
    yield
    # Clean up after test
    OPTIONS.clear()

def test_upgrade_with_uv_flag(runner, setup_function):
    """Test upgrade command with uv flag"""
    result = runner.invoke(cli, ['upgrade', '--uv'])
    assert result.exit_code == 0
    assert OPTIONS.get('use_uv') is True

def test_verify_with_uv_flag(runner, setup_function):
    """Test verify command with uv flag"""
    result = runner.invoke(cli, ['verify', '-u'])
    assert result.exit_code == 0
    assert OPTIONS.get('use_uv') is True

def test_lock_without_uv_flag(runner, setup_function):
    """Test lock command without uv flag"""
    result = runner.invoke(cli, ['lock'])
    assert result.exit_code == 0
    assert OPTIONS.get('use_uv') is False

def test_upgrade_without_uv_flag(runner, setup_function):
    """Test upgrade command without uv flag"""
    result = runner.invoke(cli, ['upgrade'])
    assert result.exit_code == 0
    assert OPTIONS.get('use_uv') is False

def test_verify_without_uv_flag(runner, setup_function):
    """Test verify command without uv flag"""
    result = runner.invoke(cli, ['verify'])
    assert result.exit_code == 0
    assert OPTIONS.get('use_uv') is False