"""Test llm-rules CLI package."""

import airules


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(airules.__version__, str)
    assert airules.__version__ == "0.1.0"