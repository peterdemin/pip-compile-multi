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
    shutil.copytree('requirements', os.path.join(tmp_dir, 'requirements'))
    shutil.copy('setup.cfg', tmp_dir)
    old_cwd = os.getcwd()
    os.chdir(tmp_dir)
    yield tmp_dir
    os.chdir(old_cwd)
    shutil.rmtree(tmp_dir)
