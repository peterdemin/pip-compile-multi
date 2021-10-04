"""Dependency parser tests"""

from pipcompilemulti.dependency import Dependency


def test_parse_package_name():
    """Simple package name with a single "via" reference."""
    dependency = Dependency("six==1.0    # via pkg")
    assert vars(dependency) == {
        "comment": "    # via pkg",
        "hashes": "",
        "is_vcs": False,
        "package": "six",
        "valid": True,
        "version": "1.0",
    }


def test_parse_url_without_postfix():
    """Package URL with package and constraint references."""
    dependency = Dependency(
        "https://site.com/path#egg=dep\n  # via\n  # -c constraint\n  # -r pkg"
    )
    assert vars(dependency) == {
        "comment": "\n  # via\n  # -c constraint\n  # -r pkg",
        "hashes": "",
        "is_vcs": True,
        "line": (
            "https://site.com/path#egg=dep\n"
            "  # via\n"
            "  # -c constraint\n"
            "  # -r pkg"
        ),
        "package": "dep",
        "valid": True,
        "version": "",
    }


def test_parse_url_with_postfix():
    """VCS URL with package and constraint references."""
    dependency = Dependency(
        'git+https://site@0.4.1'
        '#egg=dep==1.2.3_git'
        '&sub=dir'
        '\n  # via\n  # -c constraint\n  # -r pkg'
    )
    assert vars(dependency) == {
        "comment": "\n  # via\n  # -c constraint\n  # -r pkg",
        "hashes": "",
        "is_vcs": True,
        "line": (
            "git+https://site@0.4.1#egg=dep==1.2.3_git&sub=dir\n"
            "  # via\n"
            "  # -c constraint\n"
            "  # -r pkg"
        ),
        "package": "dep",
        "valid": True,
        "version": "",
    }
