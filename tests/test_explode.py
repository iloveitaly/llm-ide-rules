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
        assert not Path(".cursor/commands").exists()
        assert Path(".github/instructions").exists()
        assert not Path(".github/prompts").exists()
        assert not Path(".claude/commands").exists()
        assert not Path(".gemini/commands").exists()

        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/react.mdc").exists()

        assert Path(".github/instructions/python.instructions.md").exists()
        assert Path(".github/instructions/react.instructions.md").exists()

        content = Path(".cursor/rules/python.mdc").read_text()
        assert "Here are Python rules for development" in content
        assert "alwaysApply: true" in content
        assert "globs: \n" in content
        assert "description: Python" in content


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
        assert "globs: \n" in content
        assert "description: Custom Unmapped Section" in content
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
        assert "description: Python" in python_content
        assert "Here are Python rules" in python_content

        custom_content = Path(".cursor/rules/customsection.mdc").read_text()
        assert "**/*.custom" in custom_content
        assert "description: CustomSection" in custom_content
        assert "Here are custom rules" in custom_content


def test_explode_glob_directive_parsing():
    """Test glob directive parsing with various formats."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: **/*.py

Here are Python rules.

## React
Globs: **/*.tsx

Here are React rules (uppercase G).

## TypeScript
GLOBS: **/*.ts

Here are TypeScript rules (all caps).

## NoSpace
globs:**/*.nospace

This should NOT be parsed as a glob (missing space).

## ExtraWhitespace
globs:   **/*.whitespace

This should work with extra whitespace after colon.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        # Test lowercase "globs:"
        python_content = Path(".cursor/rules/python.mdc").read_text()
        assert "**/*.py" in python_content
        assert "description: Python" in python_content
        assert "Here are Python rules" in python_content

        # Test uppercase "Globs:"
        react_content = Path(".cursor/rules/react.mdc").read_text()
        assert "**/*.tsx" in react_content
        assert "description: React" in react_content
        assert "Here are React rules" in react_content

        # Test all caps "GLOBS:"
        typescript_content = Path(".cursor/rules/typescript.mdc").read_text()
        assert "**/*.ts" in typescript_content
        assert "description: TypeScript" in typescript_content
        assert "Here are TypeScript rules" in typescript_content

        # Test missing space - should be treated as alwaysApply (no glob pattern)
        nospace_content = Path(".cursor/rules/nospace.mdc").read_text()
        assert "alwaysApply: true" in nospace_content
        assert "description: NoSpace" in nospace_content
        assert "globs:**/*.nospace" in nospace_content  # Should keep the malformed line

        # Test extra whitespace - should still parse correctly
        whitespace_content = Path(".cursor/rules/extrawhitespace.mdc").read_text()
        assert "**/*.whitespace" in whitespace_content
        assert "description: ExtraWhitespace" in whitespace_content
        assert "This should work with extra whitespace" in whitespace_content


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
        assert "@./AGENTS.md" in claude_content

        # Check AGENTS.md
        agents_md = Path("AGENTS.md")
        assert agents_md.exists()
        agents_content = agents_md.read_text()
        assert "## Python" in agents_content
        assert "Here are Python rules." in agents_content
        assert "## Unmapped" in agents_content
        assert "Here are unmapped rules." in agents_content
