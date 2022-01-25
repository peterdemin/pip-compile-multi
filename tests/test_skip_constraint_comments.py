"""Tests for Skip constraints in comments of output files feature."""
from textwrap import dedent
from pipcompilemulti.features.skip_constraint_comments import SkipConstraintComments


_SOURCE = dedent(
    """
        # via
        #   -c path/to/sink.txt
        #   -r path/to/requirements.in
    """
).rstrip()
_EXPECTED = dedent(
    """
        # via -r path/to/requirements.in
    """
).rstrip()


class SkipConstraintCommentsAlwayOn(SkipConstraintComments):
    """Force-enabled feature."""
    enabled = True


def test_drop_sink_example():
    """Drops sink comment when using package @ url notation."""
    feature = SkipConstraintCommentsAlwayOn()
    result = feature.process_dependency_comments(_SOURCE)
    assert result == _EXPECTED
