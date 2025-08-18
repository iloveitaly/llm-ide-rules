"""Test airules."""

import airules


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(airules.__name__, str)