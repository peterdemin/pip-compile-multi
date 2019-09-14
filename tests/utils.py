"""Test utilities."""

import os
import tempfile
import shutil
import contextlib


@contextlib.contextmanager
def temp_dir():
    """Create temporary directory with copy of requirements."""
    tmp_dir = tempfile.mkdtemp()
    os.rmdir(tmp_dir)
    shutil.copytree('requirements', tmp_dir)
    yield tmp_dir
    shutil.rmtree(tmp_dir)
