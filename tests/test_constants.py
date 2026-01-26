"""Test constants module functionality."""

import json
import tempfile
from pathlib import Path

from llm_ide_rules.constants import (
    filename_to_header,
    header_to_filename,
    load_section_globs,
)


def test_header_to_filename_simple():
    """Test converting simple headers to filenames."""
    assert header_to_filename("Python") == "python"
    assert header_to_filename("React") == "react"
    assert header_to_filename("FastAPI") == "fastapi"


def test_header_to_filename_multi_word():
    """Test converting multi-word headers to filenames."""
    assert header_to_filename("React Router") == "react-router"
    assert header_to_filename("Python App") == "python-app"
    assert header_to_filename("Pytest Integration Tests") == "pytest-integration-tests"


def test_header_to_filename_already_lowercase():
    """Test converting already lowercase headers."""
    assert header_to_filename("typescript") == "typescript"
    assert header_to_filename("shell") == "shell"


def test_filename_to_header_simple():
    """Test converting simple filenames to headers."""
    assert filename_to_header("python") == "Python"
    assert filename_to_header("react") == "React"
    assert filename_to_header("fastapi") == "Fastapi"


def test_filename_to_header_multi_word():
    """Test converting multi-word filenames to headers."""
    assert filename_to_header("react-router") == "React Router"
    assert filename_to_header("python-app") == "Python App"
    assert filename_to_header("pytest-integration-tests") == "Pytest Integration Tests"


def test_filename_to_header_already_capitalized():
    """Test converting already capitalized filenames."""
    assert filename_to_header("Python") == "Python"
    assert filename_to_header("FastAPI") == "Fastapi"


def test_load_section_globs_default():
    """Test loading section globs from default config."""
    globs = load_section_globs()

    assert "Python" in globs
    assert globs["Python"] == "**/*.py"
    assert "React" in globs
    assert globs["React"] == "**/*.tsx"
    assert "FastAPI" in globs
    assert "TypeScript" in globs
    assert "Shell" in globs


def test_load_section_globs_preserves_capitalization():
    """Test that section_globs preserves special capitalization."""
    globs = load_section_globs()

    assert "FastAPI" in globs
    assert "React Router" in globs
    assert "Python App" in globs


def test_load_section_globs_custom_config():
    """Test loading section globs from custom configuration file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_config = {
            "section_globs": {
                "Python": "**/*.py",
                "CustomSection": "**/*.custom",
                "Another Section": "**/*.another",
            }
        }

        config_path = Path(temp_dir) / "custom_config.json"
        config_path.write_text(json.dumps(custom_config))

        globs = load_section_globs(str(config_path))

        assert len(globs) == 3
        assert globs["Python"] == "**/*.py"
        assert globs["CustomSection"] == "**/*.custom"
        assert globs["Another Section"] == "**/*.another"


def test_load_section_globs_custom_config_overrides_default():
    """Test that custom config completely overrides default."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_config = {"section_globs": {"OnlyThis": "**/*.only"}}

        config_path = Path(temp_dir) / "custom_config.json"
        config_path.write_text(json.dumps(custom_config))

        globs = load_section_globs(str(config_path))

        assert len(globs) == 1
        assert "OnlyThis" in globs
        assert "Python" not in globs
        assert "React" not in globs


def test_load_section_globs_nonexistent_custom_config():
    """Test loading with nonexistent custom config falls back to default."""
    globs = load_section_globs("/nonexistent/path.json")

    assert "Python" in globs
    assert "React" in globs


def test_load_section_globs_with_none_values():
    """Test that section globs can have None values for prompts."""
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_config = {
            "section_globs": {
                "Python": "**/*.py",
                "SomePrompt": None,
            }
        }

        config_path = Path(temp_dir) / "custom_config.json"
        config_path.write_text(json.dumps(custom_config))

        globs = load_section_globs(str(config_path))

        assert globs["Python"] == "**/*.py"
        assert globs["SomePrompt"] is None


def test_header_to_filename_roundtrip():
    """Test that header_to_filename and filename_to_header are symmetric for simple cases."""
    headers = ["Python", "React", "TypeScript", "FastAPI"]

    for header in headers:
        filename = header_to_filename(header)
        # Note: roundtrip won't preserve original casing for acronyms
        # This is expected behavior - filename_to_header uses title()
        result = filename_to_header(filename)
        assert result.lower() == header.lower()


def test_header_to_filename_special_characters():
    """Test that header_to_filename handles spaces correctly."""
    assert header_to_filename("My Special Rule") == "my-special-rule"
    assert (
        header_to_filename("Rule With  Multiple  Spaces")
        == "rule-with--multiple--spaces"
    )


def test_filename_to_header_special_characters():
    """Test that filename_to_header handles dashes correctly."""
    assert filename_to_header("my-special-rule") == "My Special Rule"
    assert (
        filename_to_header("rule-with--multiple--dashes")
        == "Rule With  Multiple  Dashes"
    )
