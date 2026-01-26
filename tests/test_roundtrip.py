"""Test round-trip functionality: explode → implode produces equivalent content."""

import os
import re
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

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
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


def test_roundtrip_cursor_commands():
    """Test explode → implode cursor produces equivalent commands.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix any errors that occur.

## Plan Only

Description: Plan without executing

Create a plan for the implementation.
"""
        Path("commands.md").write_text(commands_content)

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        assert Path(".cursor/commands/fix-tests.md").exists()
        assert Path(".cursor/commands/plan-only.md").exists()

        implode_result = runner.invoke(app, ["implode", "cursor"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("commands.md").read_text()

        original_sections = extract_sections(commands_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert set(original_sections.keys()) == set(roundtrip_sections.keys())

        for section_name in original_sections:
            original_normalized = normalize_whitespace(original_sections[section_name])
            roundtrip_normalized = normalize_whitespace(
                roundtrip_sections[section_name]
            )

            if section_name in ["Fix Tests", "Plan Only"]:
                original_without_desc = re.sub(
                    r"Description:.*\n\n?", "", original_normalized
                )
                assert original_without_desc.strip() in roundtrip_normalized


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

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
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


def test_roundtrip_github_prompts():
    """Test explode → implode github produces equivalent prompts."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Python instructions.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix errors.

## Debug Issue

Description: Debug an issue

Investigate and fix the issue.
"""
        Path("commands.md").write_text(commands_content)

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        assert Path(".github/prompts/fix-tests.prompt.md").exists()
        assert Path(".github/prompts/debug-issue.prompt.md").exists()

        implode_result = runner.invoke(app, ["implode", "github"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("commands.md").read_text()

        original_sections = extract_sections(commands_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert set(original_sections.keys()) == set(roundtrip_sections.keys())


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

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
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

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()

        cursor_content = Path(".cursor/rules/custom-unmapped-section.mdc").read_text()
        assert "alwaysApply: true" in cursor_content

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        original_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert "Custom Unmapped Section" in roundtrip_sections
        assert normalize_whitespace(
            original_sections["Custom Unmapped Section"]
        ) == normalize_whitespace(roundtrip_sections["Custom Unmapped Section"])


def test_roundtrip_with_custom_config():
    """Test round-trip with custom configuration file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        custom_config = """{
  "section_globs": {
    "Python": "**/*.py",
    "CustomSection": "**/*.custom"
  }
}"""
        Path("custom_config.json").write_text(custom_config)

        original_content = """# Sample Instructions

## Python

Python rules.

## CustomSection

Custom section rules.
"""

        Path("instructions.md").write_text(original_content)

        explode_result = runner.invoke(
            app, ["explode", "instructions.md", "--config", "custom_config.json"]
        )
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(
            app, ["implode", "cursor", "roundtrip.md", "--config", "custom_config.json"]
        )
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        original_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert set(original_sections.keys()) == set(roundtrip_sections.keys())


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

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(app, ["implode", "cursor", "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("roundtrip.md").read_text()

        original_sections = extract_sections(original_content)
        roundtrip_sections = extract_sections(roundtrip_content)

        assert "```python" in roundtrip_sections["Python"]
        assert "def hello(name: str)" in roundtrip_sections["Python"]
        assert "1. Use type hints" in roundtrip_sections["Python"]


def test_roundtrip_claude_commands():
    """Test explode → implode claude produces equivalent commands.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix errors.
"""
        Path("commands.md").write_text(commands_content)

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        assert Path(".claude/commands/fix-tests.md").exists()

        implode_result = runner.invoke(app, ["implode", "claude"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("commands.md").read_text()

        assert "## Fix Tests" in roundtrip_content
        assert "Run pytest and fix errors" in roundtrip_content


def test_roundtrip_gemini_commands():
    """Test explode → implode gemini produces equivalent commands.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix errors.
"""
        Path("commands.md").write_text(commands_content)

        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        assert explode_result.exit_code == 0

        assert Path(".gemini/commands/fix-tests.toml").exists()

        implode_result = runner.invoke(app, ["implode", "gemini"])
        assert implode_result.exit_code == 0

        roundtrip_content = Path("commands.md").read_text()

        assert "## Fix Tests" in roundtrip_content
        assert "Run pytest and fix errors" in roundtrip_content
