"""Feature that enables using uv instead of pip-compile.

UV is an extremely fast Python package installer and resolver written in Rust.
When enabled, pip-compile-multi will use uv's dependency resolver instead of pip-tools.

Key differences between uv and pip-tools output:

1. Annotations:
   - UV doesn't support pip-tools style annotations (via/from comments)
   - The --no-annotate flag is automatically added when using uv

2. Performance:
   - UV is significantly faster at dependency resolution
   - Particularly noticeable in large projects with complex dependency trees

3. Output Format:
   - UV produces cleaner output without header comments
   - Package versions are still pinned exactly like pip-tools
   - Hash generation (--generate-hashes) works the same way

4. Version Resolution:
   - UV may occasionally resolve to slightly different versions than pip-tools
   - Both tools respect version constraints equally
   - UV's resolver is more aggressive at finding newer versions

To use UV:
- Install uv>=0.1.0 (pip install uv)
- Use the --uv flag with commands: lock --uv, upgrade --uv, verify --uv
"""

from .base import BaseFeature


class UseUV(BaseFeature):
    """Use uv for dependency resolution.

    This feature enables using uv's fast Rust-based dependency resolver
    instead of pip-tools. UV must be installed (pip install uv>=0.1.0)
    before using this feature.
    """

    def __init__(self):
        """Initialize with disabled state."""
        self.enabled = False

    def extract_option(self, kwargs):
        """Extract use_uv option."""
        self.enabled = kwargs.pop('use_uv', False)

    def bind(self, command):
        """Add --uv option to command."""
        return command

    def get(self):
        """Return current state."""
        return self.enabled

    def set(self, value):
        """Set current state."""
        self.enabled = bool(value)
