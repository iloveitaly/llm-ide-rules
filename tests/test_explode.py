"""Test explode command functionality."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_explode_help():
    """Test that explode command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["explode", "--help"])
    assert result.exit_code == 0
    assert "Convert instruction file to separate rule files" in result.stdout
    assert "agent" in result.stdout


def test_explode_basic_functionality():
    """Test basic explode functionality with a sample instruction file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Here are Python rules for development.

## React

Here are React rules for frontend development.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0
        assert "Created files in" in result.stdout

        assert Path(".cursor/rules").exists()
        assert Path(".cursor/commands").exists()
        assert Path(".github/instructions").exists()
        assert Path(".github/prompts").exists()
        assert Path(".claude/commands").exists()
        assert Path(".gemini/commands").exists()

        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/react.mdc").exists()

        assert Path(".github/instructions/python.instructions.md").exists()
        assert Path(".github/instructions/react.instructions.md").exists()

        content = Path(".cursor/rules/python.mdc").read_text()
        assert "Here are Python rules for development" in content
        assert "alwaysApply: true" in content


def test_explode_with_commands_file():
    """Test explode with separate commands.md file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Here are Python rules for development.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests

Here are instructions to fix tests.

## Plan Only

Description: Plan without executing

Here are instructions to plan only.
"""
        Path("commands.md").write_text(commands_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        assert Path(".cursor/rules/python.mdc").exists()

        assert Path(".cursor/commands/fix-tests.md").exists()
        assert Path(".cursor/commands/plan-only.md").exists()
        assert Path(".claude/commands/fix-tests.md").exists()
        assert Path(".claude/commands/plan-only.md").exists()
        assert Path(".gemini/commands/fix-tests.toml").exists()
        assert Path(".github/prompts/fix-tests.prompt.md").exists()


def test_explode_unmapped_section_as_always_apply():
    """Test that unmapped sections in instructions.md are treated as always-apply rules."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Here are Python rules for development.

## Custom Unmapped Section

This section is not in sections.json so it should be treated as always-apply.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()

        content = Path(".cursor/rules/custom-unmapped-section.mdc").read_text()
        assert "alwaysApply: true" in content
        assert "This section is not in sections.json" in content


def test_explode_with_inline_globs():
    """Test explode with inline glob directives."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: **/*.py

Here are Python rules.

## CustomSection
globs: **/*.custom

Here are custom rules.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/customsection.mdc").exists()

        python_content = Path(".cursor/rules/python.mdc").read_text()
        assert "**/*.py" in python_content
        assert "Here are Python rules" in python_content

        custom_content = Path(".cursor/rules/customsection.mdc").read_text()
        assert "**/*.custom" in custom_content
        assert "Here are custom rules" in custom_content


def test_explode_nonexistent_file():
    """Test explode command with nonexistent input file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["explode", "nonexistent.md"])

        assert result.exit_code == 1


def test_explode_generates_root_docs():
    """Test that explode generates CLAUDE.md and GEMINI.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python

Here are Python rules.

## Unmapped

Here are unmapped rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        # Check CLAUDE.md
        claude_md = Path("CLAUDE.md")
        assert claude_md.exists()
        claude_content = claude_md.read_text()
        assert "## Python" in claude_content
        assert "Here are Python rules." in claude_content
        assert "## Unmapped" in claude_content
        assert "Here are unmapped rules." in claude_content

        # Check GEMINI.md
        gemini_md = Path("GEMINI.md")
        assert gemini_md.exists()
        gemini_content = gemini_md.read_text()
        assert "## Python" in gemini_content
        assert "Here are Python rules." in gemini_content
        assert "## Unmapped" in gemini_content
