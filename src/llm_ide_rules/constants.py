"""Shared constants for explode and implode functionality."""

VALID_AGENTS = ["cursor", "github", "claude", "gemini", "opencode", "all"]


def header_to_filename(header: str) -> str:
    """Convert a section header to a filename."""
    return header.lower().replace(" ", "-")


def filename_to_header(filename: str) -> str:
    """Convert a filename back to a section header."""
    return filename.replace("-", " ").title()
