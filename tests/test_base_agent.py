"""Test base agent utility functions."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    extract_description_and_filter_content,
    get_ordered_files,
    get_ordered_files_github,
    replace_header_with_proper_casing,
    resolve_header_from_stem,
    strip_header,
    strip_toml_metadata,
    strip_yaml_frontmatter,
    trim_content,
    write_rule_file,
)


def test_strip_yaml_frontmatter_with_frontmatter():
    """Test stripping YAML frontmatter from text."""
    text = """---
title: Test
author: Someone
---

# Content

This is the main content."""

    result = strip_yaml_frontmatter(text)
    assert result == "# Content\n\nThis is the main content."
    assert "---" not in result
    assert "title:" not in result


def test_strip_yaml_frontmatter_without_frontmatter():
    """Test stripping YAML frontmatter when none exists."""
    text = """# Content

This is the main content."""

    result = strip_yaml_frontmatter(text)
    assert result == text


def test_strip_yaml_frontmatter_malformed():
    """Test stripping malformed frontmatter (only one delimiter)."""
    text = """---
title: Test
This has no closing delimiter

# Content"""

    result = strip_yaml_frontmatter(text)
    assert result == text


def test_strip_header_with_header():
    """Test removing header from text."""
    text = """## Python

Here are Python rules for development."""

    result = strip_header(text)
    assert result == "Here are Python rules for development."
    assert "## Python" not in result


def test_strip_header_without_header():
    """Test removing header when none exists."""
    text = """Here are some rules for development."""

    result = strip_header(text)
    assert result == text


def test_strip_header_multiple_headers():
    """Test removing only first header."""
    text = """## Python

Some content

## React

More content"""

    result = strip_header(text)
    assert "## Python" not in result
    assert "## React" in result


def test_strip_toml_metadata():
    """Test extracting content from TOML command.shell block."""
    text = """[command]
shell = \"\"\"
Fix failing tests

Run pytest and fix errors
\"\"\"
"""

    result = strip_toml_metadata(text)
    assert result == "Fix failing tests\n\nRun pytest and fix errors"
    assert "[command]" not in result
    assert "shell =" not in result


def test_strip_toml_metadata_single_line():
    """Test extracting single-line shell content."""
    text = """[command]
shell = \"\"\"Fix tests\"\"\"
"""

    result = strip_toml_metadata(text)
    assert result == "Fix tests"


def test_strip_toml_metadata_with_content_after_start():
    """Test extracting content that starts on same line as opening delimiter."""
    text = """[command]
shell = \"\"\"Fix tests
and run them\"\"\"
"""

    result = strip_toml_metadata(text)
    assert "Fix tests" in result
    assert "and run them" in result


def test_strip_toml_metadata_new_format():
    """Test extracting content from TOML prompt block."""
    text = """description = "Fix failing tests"

prompt = \"\"\"
Fix failing tests

Run pytest and fix errors
\"\"\"
"""

    result = strip_toml_metadata(text)
    assert result == "Fix failing tests\n\nRun pytest and fix errors"
    assert "description =" not in result
    assert "prompt =" not in result


def test_strip_toml_metadata_invalid_returns_original():
    """Test that invalid TOML returns the original text."""
    # Invalid TOML but text we might want to preserve if it wasn't TOML to begin with
    text = """Just some plain text
without any toml structure"""
    
    result = strip_toml_metadata(text)
    assert result == text.strip()



def test_get_ordered_files():
    """Test ordering files based on section_globs key order."""
    files = [
        Path("react.mdc"),
        Path("python.mdc"),
        Path("typescript.mdc"),
        Path("unmapped.mdc"),
    ]

    section_globs_keys = ["Python", "TypeScript", "React"]

    result = get_ordered_files(files, section_globs_keys)

    assert result[0].stem == "python"
    assert result[1].stem == "typescript"
    assert result[2].stem == "react"
    assert result[3].stem == "unmapped"


def test_get_ordered_files_unmapped_at_end():
    """Test unmapped files appear at end in sorted order."""
    files = [
        Path("zebra.mdc"),
        Path("python.mdc"),
        Path("alpha.mdc"),
    ]

    section_globs_keys = ["Python"]

    result = get_ordered_files(files, section_globs_keys)

    assert result[0].stem == "python"
    assert result[1].stem == "alpha"
    assert result[2].stem == "zebra"


def test_get_ordered_files_github():
    """Test ordering GitHub instruction files with .instructions suffix."""
    files = [
        Path("react.instructions.md"),
        Path("python.instructions.md"),
        Path("typescript.instructions.md"),
    ]

    section_globs_keys = ["Python", "TypeScript", "React"]

    result = get_ordered_files_github(files, section_globs_keys)

    assert result[0].stem == "python.instructions"
    assert result[1].stem == "typescript.instructions"
    assert result[2].stem == "react.instructions"


def test_get_ordered_files_github_unmapped():
    """Test GitHub ordering with unmapped files."""
    files = [
        Path("zebra.instructions.md"),
        Path("python.instructions.md"),
        Path("alpha.instructions.md"),
    ]

    section_globs_keys = ["Python"]

    result = get_ordered_files_github(files, section_globs_keys)

    assert result[0].stem == "python.instructions"
    assert result[1].stem == "alpha.instructions"
    assert result[2].stem == "zebra.instructions"


def test_resolve_header_from_stem_exact_match():
    """Test resolving header from stem with exact match in section_globs."""
    section_globs = {"FastAPI": "**/*.py", "TypeScript": "**/*.ts"}

    assert resolve_header_from_stem("fastapi", section_globs) == "FastAPI"
    assert resolve_header_from_stem("typescript", section_globs) == "TypeScript"


def test_resolve_header_from_stem_fallback():
    """Test resolving header from stem with fallback to title-casing."""
    section_globs = {"Python": "**/*.py"}

    result = resolve_header_from_stem("react-router", section_globs)
    assert result == "React Router"


def test_resolve_header_from_stem_preserves_acronyms():
    """Test that exact matches preserve acronyms like FastAPI."""
    section_globs = {"FastAPI": "**/*.py", "SQLModel": "**/*.py"}

    assert resolve_header_from_stem("fastapi", section_globs) == "FastAPI"
    assert resolve_header_from_stem("sqlmodel", section_globs) == "SQLModel"


def test_trim_content_with_leading_trailing_empty():
    """Test removing leading and trailing empty lines."""
    content = [
        "\n",
        "\n",
        "First line\n",
        "Second line\n",
        "\n",
        "\n",
    ]

    result = trim_content(content)
    assert result == ["First line\n", "Second line\n"]


def test_trim_content_no_empty_lines():
    """Test trimming when no empty lines exist."""
    content = ["First line\n", "Second line\n"]

    result = trim_content(content)
    assert result == content


def test_trim_content_all_empty():
    """Test trimming when all lines are empty."""
    content = ["\n", "\n", "\n"]

    result = trim_content(content)
    assert result == []


def test_trim_content_preserves_middle_empty():
    """Test that middle empty lines are preserved."""
    content = [
        "\n",
        "First line\n",
        "\n",
        "Third line\n",
        "\n",
    ]

    result = trim_content(content)
    assert result == ["First line\n", "\n", "Third line\n"]


def test_write_rule_file(tmp_path):
    """Test writing a rule file with front matter and content."""
    file_path = tmp_path / "test.mdc"
    header_yaml = "---\nalwaysApply: true\n---"
    content_lines = ["\n", "## Python\n", "\n", "Use Python 3.13\n", "\n"]

    write_rule_file(file_path, header_yaml, content_lines)

    result = file_path.read_text()
    assert result.startswith("---\nalwaysApply: true\n---\n")
    assert "## Python\n" in result
    assert "Use Python 3.13\n" in result
    assert not result.endswith("\n\n")


def test_replace_header_with_proper_casing():
    """Test replacing header with properly cased version."""
    content = ["## python\n", "\n", "Some content\n"]

    result = replace_header_with_proper_casing(content, "Python")
    assert result[0] == "## Python\n"
    assert result[1] == "\n"
    assert result[2] == "Some content\n"


def test_replace_header_with_proper_casing_preserves_acronyms():
    """Test replacing header preserves acronyms."""
    content = ["## fastapi\n", "\n", "Some content\n"]

    result = replace_header_with_proper_casing(content, "FastAPI")
    assert result[0] == "## FastAPI\n"


def test_replace_header_with_proper_casing_no_header():
    """Test replacing header when no header exists."""
    content = ["Some content\n", "More content\n"]

    result = replace_header_with_proper_casing(content, "Python")
    assert result == content


def test_extract_description_and_filter_content_with_description():
    """Test extracting description from content."""
    content = [
        "\n",
        "Description: Fix failing tests\n",
        "\n",
        "Run pytest and fix errors\n",
    ]

    description, filtered = extract_description_and_filter_content(content, "Default")

    assert description == "Fix failing tests"
    assert "Description:" not in "".join(filtered)
    assert "Run pytest and fix errors\n" in filtered


def test_extract_description_and_filter_content_without_description():
    """Test extracting description when none exists."""
    content = ["\n", "Run pytest and fix errors\n"]

    description, filtered = extract_description_and_filter_content(content, "Default")

    assert description == ""
    assert filtered == ["Run pytest and fix errors\n"]


def test_extract_description_and_filter_content_skip_headers():
    """Test that headers are skipped when looking for description."""
    content = [
        "## Fix Tests\n",
        "\n",
        "Description: Fix failing tests\n",
        "\n",
        "Run pytest\n",
    ]

    description, filtered = extract_description_and_filter_content(content, "Default")

    assert description == "Fix failing tests"
    assert "## Fix Tests\n" in filtered
    assert "Description:" not in "".join(filtered)


def test_extract_description_and_filter_content_empty():
    """Test extracting description from empty content."""
    content = []

    description, filtered = extract_description_and_filter_content(content, "Default")

    assert description == ""
    assert filtered == []


def test_extract_description_and_filter_content_trims_result():
    """Test that filtered content is trimmed."""
    content = [
        "\n",
        "\n",
        "Description: Fix tests\n",
        "\n",
        "Run pytest\n",
        "\n",
        "\n",
    ]

    description, filtered = extract_description_and_filter_content(content, "Default")

    assert description == "Fix tests"
    assert filtered == ["Run pytest\n"]
