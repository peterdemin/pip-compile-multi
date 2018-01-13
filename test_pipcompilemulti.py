import os
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

import pipcompilemulti as lock


PIN = 'pycodestyle==2.3.1         # via flake8'
CMPT = 'pycodestyle~=2.3.1         # via flake8'


def test_fix_compatible_pin():
    """Test == is replaced with ~= for compatible dependencies"""
    env = lock.Environment('xxx')
    with mock.patch.dict(lock.OPTIONS, {'compatible_patterns': ['pycode*']}):
        result = env.fix_pin(PIN)
    assert result == CMPT


def test_no_fix_incompatible_pin():
    """Test dependency is left unchanged be default"""
    env = lock.Environment('')
    result = env.fix_pin(PIN)
    assert result == PIN


def test_pin_is_ommitted_if_set_to_ignore():
    """Test ignored files won't pass"""
    env = lock.Environment('', ignore=['pycodestyle'])
    result = env.fix_pin(PIN)
    assert result is None


def test_post_releases_are_truncated_by_default():
    """Test postXXX versions are truncated to release"""
    pin = 'pycodestyle==2.3.1.post2231  # via flake8'
    env = lock.Environment('')
    result = env.fix_pin(pin)
    assert result == PIN


def test_allow_post_releases():
    """Test postXXX versions are kept if allow_post=True"""
    pin = 'pycodestyle==2.3.1.post2231 # via flake8'
    env = lock.Environment('', allow_post=True)
    result = env.fix_pin(pin)
    assert result == pin


@pytest.mark.parametrize('name, refs', [
    ('base.in', []),
    ('test.in', ['base']),
    ('local.in', ['test']),
])
def test_parse_references(name, refs):
    """Check references are parsed for sample files"""
    env = lock.Environment('')
    result = env.parse_references(
        os.path.join('requirements', name)
    )
    assert result == refs