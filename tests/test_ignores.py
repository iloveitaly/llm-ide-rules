"""Test ignores command functionality."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_ignores_basic_functionality():
    """Test basic ignores functionality with a sample instruction file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: *.py

Here are Python rules for development.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md", "--print"])

        assert result.exit_code == 0
        output = result.stdout

        # Check that files are listed
        assert ".cursor/rules/python.mdc" in output
        assert ".github/instructions/python.instructions.md" in output

        # Check that files are NOT created
        assert not Path(".cursor/rules/python.mdc").exists()
        assert not Path(".github/instructions/python.instructions.md").exists()
        assert not Path(".cursor").exists()
        assert not Path(".github").exists()


def test_ignores_with_commands():
    """Test ignores with commands.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Fix Tests

Description: Fix failing tests
"""
        Path("commands.md").write_text(commands_content)

        result = runner.invoke(app, ["ignores", "instructions.md", "--print"])

        assert result.exit_code == 0
        output = result.stdout

        assert ".cursor/commands/fix-tests.md" in output
        assert ".claude/commands/fix-tests.md" in output
        assert ".github/prompts/fix-tests.prompt.md" in output

        assert not Path(".cursor").exists()


def test_ignores_missing_file():
    """Test ignores with missing file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["ignores", "nonexistent.md"])

        assert result.exit_code == 1


def test_ignores_updates_gitignore():
    """Test ignores writes to .gitignore when no print flag is provided."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)
        Path(".gitignore").write_text("node_modules/\n")

        result = runner.invoke(app, ["ignores", "instructions.md"])

        assert result.exit_code == 0
        assert "Updated .gitignore" in result.stdout

        gitignore_content = Path(".gitignore").read_text()
        assert "node_modules/" in gitignore_content
        assert "# START AI INSTRUCTION IGNORES" in gitignore_content
        assert "/.cursor/rules/python.mdc" in gitignore_content
        assert "/.github/instructions/python.instructions.md" in gitignore_content
        assert "# END AI INSTRUCTION IGNORES" in gitignore_content


def test_ignores_replaces_in_gitignore():
    """Test ignores replaces existing block in .gitignore."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        initial_gitignore = """node_modules/
# START AI INSTRUCTION IGNORES
/.cursor/rules/old.mdc
# END AI INSTRUCTION IGNORES
*.log
"""
        Path(".gitignore").write_text(initial_gitignore)

        result = runner.invoke(app, ["ignores", "instructions.md"])

        assert result.exit_code == 0
        assert "Updated .gitignore" in result.stdout

        gitignore_content = Path(".gitignore").read_text()
        assert "node_modules/" in gitignore_content
        assert "*.log" in gitignore_content
        assert "old.mdc" not in gitignore_content
        assert "/.cursor/rules/python.mdc" in gitignore_content
        assert "/.github/instructions/python.instructions.md" in gitignore_content

        # Verify only one pair of markers exists
        assert gitignore_content.count("# START AI INSTRUCTION IGNORES") == 1
        assert gitignore_content.count("# END AI INSTRUCTION IGNORES") == 1


def test_ignores_removes_from_gitignore():
    """Test ignores removes files from .gitignore when they are no longer generated."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Initial state with some files
        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md"])
        assert result.exit_code == 0
        gitignore_content = Path(".gitignore").read_text()
        assert "/.cursor/rules/python.mdc" in gitignore_content

        # Remove the section from instructions
        instructions_content_empty = """# Sample Instructions
"""
        Path("instructions.md").write_text(instructions_content_empty)

        # Run ignores again
        result = runner.invoke(app, ["ignores", "instructions.md"])
        assert result.exit_code == 0

        # Verify it's gone from .gitignore
        gitignore_content = Path(".gitignore").read_text()
        assert "/.cursor/rules/python.mdc" not in gitignore_content
        # Markers should still be there
        assert "# START AI INSTRUCTION IGNORES" in gitignore_content
        assert "# END AI INSTRUCTION IGNORES" in gitignore_content


def test_ignores_includes_general_files():
    """Test that general files are included in ignores list."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

This is some general instruction content.

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md", "--print"])

        assert result.exit_code == 0
        output = result.stdout

        assert ".cursor/rules/general.mdc" in output
        assert ".github/copilot-instructions.md" in output
        assert ".claude/rules/general.md" in output
        assert ".claude/rules/python.md" in output
        assert "AGENTS.md" in output


def test_ignores_detects_single_active_agent():
    """Test ignores automatically detects a single active agent directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".cursor").mkdir()
        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md", "--print"])

        assert result.exit_code == 0
        output = result.stdout

        assert ".cursor/rules/python.mdc" in output
        assert ".github" not in output
        assert ".claude" not in output


def test_ignores_detects_multiple_active_agents():
    """Test ignores automatically detects multiple active agent directories."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".cursor").mkdir()
        Path(".claude").mkdir()
        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md", "--print"])

        assert result.exit_code == 0
        output = result.stdout

        assert ".cursor/rules/python.mdc" in output
        assert ".claude/rules/python.md" in output
        assert ".github" not in output


def test_ignores_explicit_agent_overrides_detection():
    """Test that explicit --agent overrides active agent detection."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".cursor").mkdir()
        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(
            app, ["ignores", "instructions.md", "--agent", "github", "--print"]
        )

        assert result.exit_code == 0
        output = result.stdout

        assert ".github/instructions/python.instructions.md" in output
        assert ".cursor" not in output


def test_ignores_echoes_detected_agents_when_not_print():
    """Test that ignores echoes detected active agents when writing .gitignore."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".cursor").mkdir()
        instructions_content = """# Sample Instructions

## Python
globs: *.py

Python rules.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md"])

        assert result.exit_code == 0
        assert "Detected active agents: cursor" in result.stdout
        assert "Updated .gitignore" in result.stdout

