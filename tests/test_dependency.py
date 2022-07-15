"""Dependency parser tests"""

from pipcompilemulti.dependency import Dependency
from pipcompilemulti.features import FEATURES
from pipcompilemulti.options import OPTIONS


def test_parse_package_name():
    """Simple package name with a single "via" reference."""
    dependency = Dependency("six==1.0    # via pkg")
    assert vars(dependency) == {
        "is_at": False,
        "is_vcs": False,
        "comment": "    # via pkg",
        "comment_span": (8, 21),
        "hashes": "",
        "package": "six",
        "valid": True,
        "version": "1.0",
        "markers": "",
        "line": "six==1.0    # via pkg",
    }
    OPTIONS[FEATURES.skip_constraint_comments.OPTION_NAME] = True
    assert dependency.serialize() == "six==1.0                  # via pkg"


def test_parse_url_without_postfix():
    """Package URL with package and constraint references."""
    dependency = Dependency(
        "https://site.com/path#egg=dep\n  # via\n  # -c constraint\n  # -r pkg"
    )
    assert vars(dependency) == {
        "is_at": False,
        "is_vcs": True,
        "comment": "\n  # via\n  # -c constraint\n  # -r pkg",
        "comment_span": (29, 66),
        "hashes": "",
        "line": (
            "https://site.com/path#egg=dep\n"
            "  # via\n"
            "  # -c constraint\n"
            "  # -r pkg"
        ),
        "package": "dep",
        "valid": True,
        "markers": "",
        "version": "",
    }


def test_parse_url_with_postfix():
    """VCS URL with package and constraint references."""
    dependency = Dependency(
        "git+https://site@0.4.1#egg=dep==1.2.3_git&sub=dir"
        "\n  # via\n  # -c constraint\n  # -r pkg"
    )
    assert vars(dependency) == {
        "is_at": False,
        "is_vcs": True,
        "comment": "\n  # via\n  # -c constraint\n  # -r pkg",
        "comment_span": (49, 86),
        "hashes": "",
        "line": (
            "git+https://site@0.4.1#egg=dep==1.2.3_git&sub=dir\n"
            "  # via\n"
            "  # -c constraint\n"
            "  # -r pkg"
        ),
        "package": "dep",
        "valid": True,
        "version": "",
        "markers": "",
    }
    OPTIONS[FEATURES.skip_constraint_comments.OPTION_NAME] = True
    assert dependency.serialize() == (
        "git+https://site@0.4.1#egg=dep==1.2.3_git&sub=dir\n" "  # via -r pkg"
    )


def test_parse_at_url_notation():
    """Package URL with package and constraint references."""
    dependency = Dependency(
        "dep @ https://site.com/path\n  # via\n  # -c constraint\n  # -r pkg"
    )
    assert vars(dependency) == {
        "is_at": True,
        "is_vcs": False,
        "comment": "\n  # via\n  # -c constraint\n  # -r pkg",
        "comment_span": (27, 64),
        "hashes": "",
        "line": (
            "dep @ https://site.com/path\n"
            "  # via\n"
            "  # -c constraint\n"
            "  # -r pkg"
        ),
        "package": "dep",
        "valid": True,
        "version": "",
        "markers": "",
    }
    OPTIONS[FEATURES.skip_constraint_comments.OPTION_NAME] = True
    assert dependency.serialize() == ("dep @ https://site.com/path\n" "  # via -r pkg")


def test_sanitize_package_version():
    """Simple package name with leading zeros in the version, with a single "via" reference."""
    dependency = Dependency("gcsfs==2022.02.1    # via pkg")
    assert vars(dependency) == {
        "is_at": False,
        "is_vcs": False,
        "comment": "    # via pkg",
        "comment_span": (16, 29),
        "hashes": "",
        "package": "gcsfs",
        "valid": True,
        "version": "2022.2.1",
        "markers": "",
        "line": "gcsfs==2022.02.1    # via pkg",
    }
    OPTIONS[FEATURES.skip_constraint_comments.OPTION_NAME] = True
    assert dependency.serialize() == "gcsfs==2022.2.1           # via pkg"


def test_parse_sys_platform():
    """Package URL with package and constraint references."""
    dependency = Dependency('dep==1 ; sys_platform == "darwin" # Comment')
    assert vars(dependency) == {
        "line": 'dep==1 ; sys_platform == "darwin" # Comment',
        "valid": True,
        "is_at": False,
        "is_vcs": False,
        "package": "dep",
        "version": "1",
        "markers": ' ; sys_platform == "darwin"',
        "hashes": "",
        "comment": " # Comment",
        "comment_span": (33, 43),
    }
    OPTIONS[FEATURES.skip_constraint_comments.OPTION_NAME] = True
    assert dependency.serialize() == ('dep==1 ; sys_platform == "darwin"  # Comment')
