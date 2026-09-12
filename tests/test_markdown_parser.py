"""Test markdown parsing utilities."""

from llm_ide_rules.markdown_parser import (
    extract_glob_directive,
    filter_markdown_by_globs,
    parse_sections,
)


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
    """Test glob directive without space after colon should be parsed."""
    content = ["## Python\n", "globs:**/*.py\n", "\n", "Some content\n"]
    filtered, pattern = extract_glob_directive(content)

    assert pattern == "**/*.py"
    assert "globs:**/*.py\n" not in filtered
    assert "Some content\n" in filtered


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

    _general, sections = parse_sections(text)

    python_section = sections["Python"]
    assert python_section.glob_pattern is None
    assert "Python content" in "".join(python_section.content)

    react_section = sections["React"]
    assert react_section.glob_pattern is None


def test_filter_markdown_by_globs_single_exclude():
    """Test excluding sections matching a single glob pattern."""
    text = """# Instructions
General rules.

## Python
globs: **/*.py

Python rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, ["**/*.py"])

    assert omitted == ["Python"]
    assert "## Python" not in filtered
    assert "Python rules." not in filtered
    assert "## React" in filtered
    assert "globs: **/*.tsx" in filtered
    assert "React rules." in filtered
    assert "General rules." in filtered


def test_filter_markdown_by_globs_comma_separated_exclude():
    """Test excluding sections using comma-separated glob patterns."""
    text = """# Instructions
General rules.

## Alembic Migrations
globs: migrations/versions/*.py

Migration rules.

## Fastapi
globs: app/routes/**/*.py

Fastapi rules.

## Shell
globs: **/*.sh

Shell rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, ["*.py,**/*.py"])

    assert "Alembic Migrations" in omitted
    assert "Fastapi" in omitted
    assert "## Alembic Migrations" not in filtered
    assert "## Fastapi" not in filtered
    assert "## Shell" in filtered
    assert "Shell rules." in filtered


def test_filter_markdown_by_globs_partial_match_preserved():
    """Test sections with multiple globs are preserved if not all globs match."""
    text = """# Instructions

## Typescript
globs: **/*.ts,**/*.tsx

TS rules.

## React
globs: **/*.tsx

React rules.
"""
    # Only excluding ts, so Typescript section should be preserved because tsx is not excluded
    filtered, omitted = filter_markdown_by_globs(text, ["**/*.ts"])

    assert omitted == []
    assert "## Typescript" in filtered
    assert "globs: **/*.ts,**/*.tsx" in filtered
    assert "## React" in filtered


def test_filter_markdown_by_globs_full_match_omitted():
    """Test sections with multiple globs are omitted when all globs match."""
    text = """# Instructions

## Typescript
globs: **/*.ts,**/*.tsx

TS rules.

## React
globs: **/*.tsx

React rules.
"""
    # Both ts and tsx excluded, so Typescript section matches in full and is omitted
    filtered, omitted = filter_markdown_by_globs(text, ["**/*.ts,**/*.tsx"])

    assert "Typescript" in omitted
    assert "React" in omitted
    assert "## Typescript" not in filtered
    assert "## React" not in filtered


def test_filter_markdown_by_globs_no_glob_preserved():
    """Test sections without globs are always preserved."""
    text = """# Instructions

## General Coding
Some general coding instructions without glob.

## Python
globs: **/*.py

Python rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, ["**/*.py"])

    assert omitted == ["Python"]
    assert "## General Coding" in filtered
    assert "Some general coding instructions without glob." in filtered
    assert "## Python" not in filtered


def test_filter_markdown_by_globs_empty_or_none():
    """Test empty or None exclude_globs leaves markdown unchanged."""
    text = """# Instructions

## Python
globs: **/*.py

Python rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, [])
    assert filtered == text
    assert omitted == []


def test_filter_markdown_by_globs_single_include():
    """Test including sections matching a single glob pattern."""
    text = """# Instructions
General rules.

## Python
globs: **/*.py

Python rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, include_globs=["**/*.py"])

    assert omitted == ["React"]
    assert "## Python" in filtered
    assert "Python rules." in filtered
    assert "## React" not in filtered
    assert "React rules." not in filtered
    assert "General rules." in filtered


def test_filter_markdown_by_globs_comma_separated_include():
    """Test including sections using comma-separated glob patterns."""
    text = """# Instructions
General rules.

## Python
globs: **/*.py

Python rules.

## Shell
globs: **/*.sh

Shell rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(
        text, include_globs=["*.py,**/*.sh"]
    )

    assert omitted == ["React"]
    assert "## Python" in filtered
    assert "## Shell" in filtered
    assert "## React" not in filtered


def test_filter_markdown_by_globs_include_partial_match_preserved():
    """Test sections with multiple globs are included if at least one matches."""
    text = """# Instructions

## Typescript
globs: **/*.ts,**/*.tsx

TS rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, include_globs=["**/*.ts"])

    assert omitted == ["React"]
    assert "## Typescript" in filtered
    assert "TS rules." in filtered
    assert "## React" not in filtered


def test_filter_markdown_by_globs_include_unglobbed_omitted_without_wildcard():
    """Test unglobbed sections are omitted when include_globs lacks a wildcard."""
    text = """# Instructions
General rules.

## General Coding
Some general coding instructions without glob.

## Python
globs: **/*.py

Python rules.
"""
    filtered, omitted = filter_markdown_by_globs(text, include_globs=["**/*.py"])

    assert omitted == ["General Coding"]
    assert "General rules." in filtered
    assert "## General Coding" not in filtered
    assert "## Python" in filtered


def test_filter_markdown_by_globs_include_unglobbed_preserved_with_wildcard():
    """Test unglobbed sections are preserved when include_globs contains a wildcard."""
    text = """# Instructions
General rules.

## General Coding
Some general coding instructions without glob.

## Typescript
globs: **/*.ts

TS rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(
        text, include_globs=["*,*.ts"]
    )

    assert omitted == ["React"]
    assert "General rules." in filtered
    assert "## General Coding" in filtered
    assert "Some general coding instructions without glob." in filtered
    assert "## Typescript" in filtered
    assert "## React" not in filtered


def test_filter_markdown_by_globs_both_include_and_exclude():
    """Test combining include and exclude globs."""
    text = """# Instructions

## Alembic Migrations
globs: migrations/versions/*.py

Migration rules.

## Python
globs: **/*.py

Python rules.

## React
globs: **/*.tsx

React rules.
"""
    filtered, omitted = filter_markdown_by_globs(
        text,
        exclude_globs=["migrations/versions/*.py"],
        include_globs=["**/*.py"],
    )

    assert "React" in omitted
    assert "Alembic Migrations" in omitted
    assert "## Alembic Migrations" not in filtered
    assert "## React" not in filtered
    assert "## Python" in filtered

