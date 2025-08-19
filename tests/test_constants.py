"""Test constants and configuration functionality."""

import tempfile
import json
from pathlib import Path

from airules.constants import load_section_globs, header_to_filename, filename_to_header


def test_load_section_globs_default():
    """Test loading default section globs."""
    section_globs = load_section_globs()
    
    # Check that we get a dictionary
    assert isinstance(section_globs, dict)
    
    # Check that expected sections are present
    expected_sections = ["Python", "React", "TypeScript", "Shell"]
    for section in expected_sections:
        assert section in section_globs
    
    # Check that glob patterns are strings or None
    for section, pattern in section_globs.items():
        assert pattern is None or isinstance(pattern, str)


def test_load_section_globs_custom():
    """Test loading custom section globs from file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create custom config file
        custom_config = {
            "section_globs": {
                "Python": "**/*.py",
                "CustomSection": "**/*.custom",
                "PromptSection": None
            }
        }
        
        config_path = Path(temp_dir) / "custom_config.json"
        with open(config_path, "w") as f:
            json.dump(custom_config, f)
        
        # Load custom config
        section_globs = load_section_globs(str(config_path))
        
        # Check that custom config is loaded
        assert "CustomSection" in section_globs
        assert section_globs["CustomSection"] == "**/*.custom"
        assert section_globs["PromptSection"] is None
        assert len(section_globs) == 3


def test_load_section_globs_nonexistent_custom():
    """Test loading section globs with nonexistent custom file falls back to default."""
    section_globs = load_section_globs("/nonexistent/path.json")
    
    # Should fall back to default config
    assert isinstance(section_globs, dict)
    assert "Python" in section_globs


def test_header_to_filename():
    """Test conversion from header to filename."""
    assert header_to_filename("Python") == "python"
    assert header_to_filename("React Router") == "react-router"
    assert header_to_filename("TypeScript DocString") == "typescript-docstring"
    assert header_to_filename("FastAPI") == "fastapi"


def test_filename_to_header():
    """Test conversion from filename to header."""
    assert filename_to_header("python") == "Python"
    assert filename_to_header("react-router") == "React Router"
    assert filename_to_header("typescript-docstring") == "Typescript Docstring"
    assert filename_to_header("fastapi") == "Fastapi"


def test_header_filename_roundtrip():
    """Test that header to filename conversion is reversible for simple cases."""
    headers = ["Python", "React", "TypeScript", "Shell"]
    
    for header in headers:
        filename = header_to_filename(header)
        # Note: The reverse conversion won't be identical for multi-word headers
        # due to title casing, but should be functionally equivalent
        back_to_header = filename_to_header(filename)
        assert back_to_header.lower() == header.lower()


def test_section_globs_json_structure():
    """Test that the bundled section_globs.json has correct structure."""
    from airules.constants import load_section_globs
    
    # Load default config (should come from bundled JSON)
    section_globs = load_section_globs()
    
    # Check structure
    assert isinstance(section_globs, dict)
    assert len(section_globs) > 0
    
    # Check that we have a mix of glob patterns and None values
    has_globs = any(v is not None for v in section_globs.values())
    has_none = any(v is None for v in section_globs.values())
    assert has_globs, "Should have some glob patterns"
    assert has_none, "Should have some None values for prompts"


def test_section_globs_json_file_exists():
    """Test that the bundled section_globs.json file exists and is valid."""
    import json
    from pathlib import Path
    
    # Check that the JSON file exists
    json_path = Path(__file__).parent.parent / "src" / "airules" / "section_globs.json"
    assert json_path.exists(), f"section_globs.json not found at {json_path}"
    
    # Check that it's valid JSON
    with open(json_path, "r") as f:
        config = json.load(f)
    
    assert "section_globs" in config
    assert isinstance(config["section_globs"], dict)