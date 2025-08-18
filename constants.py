#!/usr/bin/env python3
"""
Shared constants for explode and implode scripts.
"""

# Mapping of section headers to their file globs or None for prompts
# The order of keys determines the order in imploded files
SECTION_GLOBS = {
    "Python": "**/*.py",
    "Python App": "**/*.py",
    "Pytest Integration Tests": "tests/integration/**/*.py",
    "Pytest Tests": "tests/**/*.py",
    "Python Route Tests": "tests/routes/**/*.py",
    "Alembic Migrations": "migrations/versions/*.py",
    "FastAPI": "app/routes/**/*.py",

    "React": "**/*.tsx",
    "React Router": "web/app/routes/**/*.tsx",
    "React Router Client Loader": None,

    "Shell": "**/*.sh",
    "TypeScript": "**/*.ts,**/*.tsx",
    "TypeScript DocString": None,

    # prompts (None indicates it's a prompt, not an instruction)
    "Secrets": None,
}

def header_to_filename(header):
    """Convert a section header to a filename."""
    return header.lower().replace(' ', '-')

def filename_to_header(filename):
    """Convert a filename back to a section header."""
    return filename.replace('-', ' ').title()
