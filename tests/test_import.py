"""Test llm-rules CLI package."""

import llm_ide_rules


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(llm_ide_rules.__version__, str)
    assert llm_ide_rules.__version__ == "0.1.0"