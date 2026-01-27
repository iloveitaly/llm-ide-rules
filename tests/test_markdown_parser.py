"""Test markdown parsing utilities."""

from llm_ide_rules.markdown_parser import extract_glob_directive, parse_sections


def test_extract_glob_directive_lowercase():
    """Test glob directive with lowercase 'globs:'."""
    content = ["## Python\n", "globs: **/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "globs: **/*.py\n" not in filtered
    assert "## Python\n" in filtered
    assert "Some content\n" in filtered


def test_extract_glob_directive_uppercase():
    """Test glob directive with uppercase 'GLOBS:'."""
    content = ["## Python\n", "GLOBS: **/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "GLOBS: **/*.py\n" not in filtered


def test_extract_glob_directive_mixed_case():
    """Test glob directive with mixed case 'Globs:'."""
    content = ["## Python\n", "Globs: **/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "Globs: **/*.py\n" not in filtered


def test_extract_glob_directive_no_space():
    """Test glob directive without space after colon should NOT be parsed."""
    content = ["## Python\n", "globs:**/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern is None
    assert "globs:**/*.py\n" in filtered  # Should keep the malformed line


def test_extract_glob_directive_extra_whitespace():
    """Test glob directive with extra whitespace after colon."""
    content = ["## Python\n", "globs:   **/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "globs:   **/*.py\n" not in filtered


def test_extract_glob_directive_with_empty_lines():
    """Test glob directive with empty lines between header and directive."""
    content = ["## Python\n", "\n", "\n", "globs: **/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "globs: **/*.py\n" not in filtered


def test_extract_glob_directive_manual():
    """Test glob directive with 'manual' value."""
    content = ["## Python\n", "globs: manual\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "manual"
    assert "globs: manual\n" not in filtered


def test_extract_glob_directive_missing():
    """Test content without glob directive."""
    content = ["## Python\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern is None
    assert filtered == content


def test_extract_glob_directive_no_header():
    """Test content without header."""
    content = ["Some content\n", "globs: **/*.py\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern is None
    assert filtered == content


def test_parse_sections_with_globs():
    """Test parse_sections extracts glob patterns correctly."""
    text = """# Title

General content here.

## Python
globs: **/*.py

Python content.

## React
globs: **/*.tsx

React content.
"""

    general, sections = parse_sections(text)

    assert "General content here" in "".join(general)
    assert "Python" in sections
    assert "React" in sections

    python_section = sections["Python"]
    assert python_section.glob_pattern == "**/*.py"
    assert "Python content" in "".join(python_section.content)
    assert "globs: **/*.py" not in "".join(python_section.content)

    react_section = sections["React"]
    assert react_section.glob_pattern == "**/*.tsx"
    assert "React content" in "".join(react_section.content)


def test_parse_sections_without_globs():
    """Test parse_sections with sections that have no glob directives."""
    text = """# Title

## Python

Python content.

## React

React content.
"""

    general, sections = parse_sections(text)

    python_section = sections["Python"]
    assert python_section.glob_pattern is None
    assert "Python content" in "".join(python_section.content)

    react_section = sections["React"]
    assert react_section.glob_pattern is None
