"""Test round-trip functionality: explode → implode produces equivalent content."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    lines = text.strip().split("\n")
    normalized_lines = [line.rstrip() for line in lines]
    while normalized_lines and not normalized_lines[-1]:
        normalized_lines.pop()
    return "\n".join(normalized_lines)


def extract_sections(text: str) -> dict[str, str]:
    """Extract sections from markdown text for easier comparison."""
    # Strip the cloned instructions marker if present
    marker = "<!-- END CLONED INSTRUCTIONS -->"
    if marker in text:
        text = text.split(marker, 1)[0]

    sections = {}
    current_section = None
    current_content = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def test_roundtrip_cursor_instructions():
    """Test explode → implode cursor produces equivalent instructions.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Here are Python rules for development.

Use Python 3.13 and prefer Pathlib.

## React

Here are React rules for frontend development.

Use functional components and hooks.

## TypeScript

Here are TypeScript rules.

Use strict mode.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "cursor"])
        assert explode_result.exit_code == 0

        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/react.mdc").exists()
        assert Path(".cursor/rules/typescript.mdc").exists()

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        original_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert set(original_sections.keys()) == set(roundtrip_sections.keys())

        for section_name in original_sections:
            assert normalize_whitespace(
                original_sections[section_name]
            ) == normalize_whitespace(roundtrip_sections[section_name])


def test_roundtrip_github_instructions():
    """Test explode → implode github produces equivalent instructions.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Here are Python instructions for development.

Follow PEP 8.

## React

Here are React instructions for frontend development.

Use JSX syntax.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "github"])
        assert explode_result.exit_code == 0

        assert Path(".github/instructions/python.instructions.md").exists()
        assert Path(".github/instructions/react.instructions.md").exists()

        implode_result = runner.invoke(app, ["implode", "github", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        original_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert set(original_sections.keys()) == set(roundtrip_sections.keys())

        for section_name in original_sections:
            assert normalize_whitespace(
                original_sections[section_name]
            ) == normalize_whitespace(roundtrip_sections[section_name])


def test_roundtrip_preserves_section_order():
    """Test that round-trip reorders sections based on section_globs."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Python rules.

## TypeScript

TypeScript rules.

## React

React rules.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "cursor"])
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        python_pos = roundtrip_content.find("## Python")
        typescript_pos = roundtrip_content.find("## TypeScript")
        react_pos = roundtrip_content.find("## React")

        # All sections should be present
        assert python_pos != -1
        assert typescript_pos != -1
        assert react_pos != -1

        # React comes before TypeScript in section_globs
        assert react_pos < typescript_pos


def test_roundtrip_with_unmapped_sections():
    """Test round-trip with sections not in section_globs (always-apply rules)."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Python rules.

## Custom Unmapped Section

This section is not in sections.json.

It should be treated as always-apply.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "cursor"])
        assert explode_result.exit_code == 0

        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()

        cursor_content = Path(".cursor/rules/custom-unmapped-section.mdc").read_text()
        assert "alwaysApply: true" in cursor_content

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        orig_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert "Custom Unmapped Section" in roundtrip_sections
        assert normalize_whitespace(
            orig_sections["Custom Unmapped Section"]
        ) == normalize_whitespace(roundtrip_sections["Custom Unmapped Section"])


def test_roundtrip_preserves_multiline_content():
    """Test that round-trip preserves multi-line and formatted content."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Here are Python rules:

1. Use type hints
2. Follow PEP 8
3. Write docstrings

Example:

```python
def hello(name: str) -> str:
    return f"Hello, {name}"
```

That's all.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "cursor"])
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        roundtrip_sections = extract_sections(roundtrip_content)

        assert "```python" in roundtrip_sections["Python"]
        assert "def hello(name: str)" in roundtrip_sections["Python"]
        assert "1. Use type hints" in roundtrip_sections["Python"]


def test_roundtrip_claude_preserves_globs():
    """Test explode -> implode claude preserves scoped rule globs."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## TypeScript
globs: web/**/*.ts

Here are TypeScript rules.

## Python

Here are Python rules.
"""
        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "claude"])
        assert explode_result.exit_code == 0

        assert Path(".claude/rules/typescript.md").exists()

        implode_result = runner.invoke(app, ["implode", "claude", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()
        roundtrip_sections = extract_sections(roundtrip_content)

        assert "globs: web/**/*.ts" in roundtrip_sections["TypeScript"]
        assert "Here are TypeScript rules." in roundtrip_sections["TypeScript"]
        assert "Here are Python rules." in roundtrip_sections["Python"]


def test_roundtrip_opencode_instructions():
    """Test explode → implode opencode produces equivalent instructions via AGENTS.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """# Sample Instructions

## Python

Python rules.
"""
        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(app, ["explode", "opencode"])
        assert explode_result.exit_code == 0

        assert Path("AGENTS.md").exists()
        assert not Path(".opencode").exists()

        implode_result = runner.invoke(app, ["implode", "opencode", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()
        assert "## Python" in roundtrip_content
        assert "Python rules." in roundtrip_content
