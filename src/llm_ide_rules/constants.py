"""Shared constants for explode and implode functionality."""

import json
from pathlib import Path

VALID_AGENTS = ["cursor", "github", "claude", "gemini", "opencode", "all"]


def load_section_globs(custom_config_path: str | None = None) -> dict[str, str | None]:
    """Load section globs from JSON config file.

    Args:
        custom_config_path: Path to custom configuration file to override defaults

    Returns:
        Dictionary mapping section headers to their file globs or None for prompts
    """
    if custom_config_path and Path(custom_config_path).exists():
        config_path = Path(custom_config_path)
    else:
        config_path = Path(__file__).parent / "sections.json"

    config = json.loads(config_path.read_text())

    return config["section_globs"]


# Default section globs - loaded from bundled JSON
SECTION_GLOBS = load_section_globs()


def header_to_filename(header: str) -> str:
    """Convert a section header to a filename."""
    return header.lower().replace(" ", "-")


def filename_to_header(filename: str) -> str:
    """Convert a filename back to a section header."""
    return filename.replace("-", " ").title()
