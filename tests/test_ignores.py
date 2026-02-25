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

Here are Python rules for development.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["ignores", "instructions.md"])

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

        result = runner.invoke(app, ["ignores", "instructions.md"])

        assert result.exit_code == 0
        output = result.stdout

        assert ".cursor/commands/fix-tests.md" in output
        assert ".claude/commands/fix-tests.md" in output
        assert ".gemini/commands/fix-tests.toml" in output
        assert ".github/prompts/fix-tests.prompt.md" in output

        assert not Path(".cursor").exists()


def test_ignores_missing_file():
    """Test ignores with missing file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["ignores", "nonexistent.md"])

        assert result.exit_code == 1
        # The error should be printed to stderr
        # CliRunner captures both by default in stdout unless mix_stderr=False?
        # But typer.echo(err=True) goes to stderr.
        # My implementation prints to sys.stderr which CliRunner should capture.

        # Since I re-raise the exception, Typer handles the exit code.
        # And I print the captured stderr.

        # Wait, explode calls `typer.Exit(1)`.
        # My ignores code catches it, prints captured stderr, and re-raises.
        # So CliRunner should see exit code 1.
