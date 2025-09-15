"""Test llm-rules CLI package."""

import re

import llm_ide_rules


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(llm_ide_rules.__version__, str)
    assert re.fullmatch(
        r"\d+\.\d+\.\d+(?:[.-][0-9A-Za-z]+)*", llm_ide_rules.__version__
    )
