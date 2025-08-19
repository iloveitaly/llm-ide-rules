"""Shared constants for explode and implode functionality."""

import json
import os
from pathlib import Path

def load_section_globs(custom_config_path: str = None) -> dict:
    """Load section globs from JSON config file.
    
    Args:
        custom_config_path: Path to custom configuration file to override defaults
    
    Returns:
        Dictionary mapping section headers to their file globs or None for prompts
    """
    if custom_config_path and os.path.exists(custom_config_path):
        config_path = Path(custom_config_path)
    else:
        # Load default bundled config
        config_path = Path(__file__).parent / "sections.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config["section_globs"]

# Default section globs - loaded from bundled JSON
SECTION_GLOBS = load_section_globs()

def header_to_filename(header):
    """Convert a section header to a filename."""
    return header.lower().replace(' ', '-')

def filename_to_header(filename):
    """Convert a filename back to a section header."""
    return filename.replace('-', ' ').title()