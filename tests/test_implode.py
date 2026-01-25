"""Test implode command functionality."""

import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner

from llm_ide_rules import app


def test_implode_help():
    """Test that implode command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "--help"])
    assert result.exit_code == 0
    assert "Bundle rule files into a single instruction file" in result.stdout


def test_implode_cursor_help():
    """Test that implode cursor subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "cursor", "--help"])
    assert result.exit_code == 0
    assert "Bundle Cursor rules" in result.stdout
    assert "config" in result.stdout


def test_implode_github_help():
    """Test that implode github subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "github", "--help"])
    assert result.exit_code == 0
    assert "Bundle GitHub" in result.stdout
    assert "config" in result.stdout


def test_implode_cursor_basic_functionality():
    """Test basic implode cursor functionality."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .cursor/rules directory with sample files
        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)

        # Create sample rule files
        with open(cursor_rules_dir / "python.mdc", "w") as f:
            f.write("""---
name: Python
description: Python development rules
pattern: "**/*.py"
---

Here are Python rules for development.""")

        with open(cursor_rules_dir / "react.mdc", "w") as f:
            f.write("""---
name: React
description: React development rules
pattern: "**/*.tsx"
---

Here are React rules for frontend development.""")

        # Run implode cursor command
        result = runner.invoke(app, ["implode", "cursor", "bundled.md"])

        # Check command succeeds
        assert result.exit_code == 0
        assert "Bundled cursor rules into bundled.md" in result.stdout

        # Check that output file was created
        assert Path("bundled.md").exists()

        # Check output file content
        with open("bundled.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert "## React" in content
            assert "Here are Python rules for development" in content
            assert "Here are React rules for frontend development" in content


def test_implode_cursor_with_commands():
    """Test implode cursor with both rules and commands."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .cursor/rules directory with sample files
        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)

        with open(cursor_rules_dir / "python.mdc", "w") as f:
            f.write("""---
name: Python
---

Python rules.""")

        # Create .cursor/commands directory with sample files
        cursor_commands_dir = Path(".cursor/commands")
        cursor_commands_dir.mkdir(parents=True)

        with open(cursor_commands_dir / "fix-tests.md", "w") as f:
            f.write("Here are instructions to fix tests.")

        # Run implode cursor command
        result = runner.invoke(app, ["implode", "cursor"])

        # Check command succeeds
        assert result.exit_code == 0

        # Check that both output files were created
        assert Path("instructions.md").exists()
        assert Path("commands.md").exists()

        # Check instructions.md content (rules only)
        with open("instructions.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert "Python rules." in content

        # Check commands.md content (commands only)
        with open("commands.md", "r") as f:
            content = f.read()
            assert "## Fix Tests" in content
            assert "Here are instructions to fix tests." in content


def test_implode_github_basic_functionality():
    """Test basic implode github functionality."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .github/instructions directory with sample files
        github_instructions_dir = Path(".github/instructions")
        github_instructions_dir.mkdir(parents=True)

        # Create sample instruction files
        with open(github_instructions_dir / "python.instructions.md", "w") as f:
            f.write("""---
pattern: "**/*.py"
---

## Python

Here are Python instructions for development.""")

        with open(github_instructions_dir / "react.instructions.md", "w") as f:
            f.write("""---
pattern: "**/*.tsx"
---

## React

Here are React instructions for frontend development.""")

        # Run implode github command
        result = runner.invoke(app, ["implode", "github", "bundled-github.md"])

        # Check command succeeds
        assert result.exit_code == 0
        assert "Bundled github instructions into bundled-github.md" in result.stdout

        # Check that output file was created
        assert Path("bundled-github.md").exists()

        # Check output file content
        with open("bundled-github.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert "## React" in content
            assert "Here are Python instructions for development" in content
            assert "Here are React instructions for frontend development" in content


def test_implode_github_with_prompts():
    """Test implode github with both instructions and prompts."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .github/instructions directory
        github_instructions_dir = Path(".github/instructions")
        github_instructions_dir.mkdir(parents=True)

        with open(github_instructions_dir / "python.instructions.md", "w") as f:
            f.write("""---
pattern: "**/*.py"
---

## Python

Python instructions.""")

        # Create .github/prompts directory
        github_prompts_dir = Path(".github/prompts")
        github_prompts_dir.mkdir(parents=True)

        with open(github_prompts_dir / "fix-tests.prompt.md", "w") as f:
            f.write("""---
mode: 'agent'
description: 'Fix tests'
---

Here are instructions to fix tests.""")

        # Run implode github command
        result = runner.invoke(app, ["implode", "github"])

        # Check command succeeds
        assert result.exit_code == 0

        # Check that both output files were created
        assert Path("instructions.md").exists()
        assert Path("commands.md").exists()

        # Check instructions.md content
        with open("instructions.md", "r") as f:
            content = f.read()
            assert "## Python" in content

        # Check commands.md content (prompts)
        with open("commands.md", "r") as f:
            content = f.read()
            assert "## Fix Tests" in content


def test_implode_cursor_missing_directory():
    """Test implode cursor with missing .cursor/rules directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run implode cursor command without creating rules directory
        result = runner.invoke(app, ["implode", "cursor", "bundled.md"])

        # Should fail with error
        assert result.exit_code == 1


def test_implode_github_missing_directory():
    """Test implode github with missing .github/instructions directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run implode github command without creating instructions directory
        result = runner.invoke(app, ["implode", "github", "bundled.md"])

        # Should fail with error
        assert result.exit_code == 1


def test_implode_with_custom_config():
    """Test implode cursor with custom configuration file."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create custom config JSON
        custom_config = """{
  "section_globs": {
    "Python": "**/*.py",
    "CustomSection": "**/*.custom"
  }
}"""
        with open("custom_config.json", "w") as f:
            f.write(custom_config)

        # Create .cursor/rules directory with sample files
        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)

        with open(cursor_rules_dir / "python.mdc", "w") as f:
            f.write("""---
name: Python
---

Python rules.""")

        with open(cursor_rules_dir / "customsection.mdc", "w") as f:
            f.write("""---
name: CustomSection
---

Custom rules.""")

        # Run implode cursor command with custom config
        result = runner.invoke(app, ["implode", "cursor", "bundled.md", "--config", "custom_config.json"])

        # Check command succeeds
        assert result.exit_code == 0

        # Check that output file contains sections in the correct order
        with open("bundled.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert "## CustomSection" in content


def test_implode_main_no_args():
    """Test implode main function with no arguments shows usage."""
    runner = CliRunner()

    result = runner.invoke(app, ["implode"])

    # Should show usage information (exit code 2 for missing command)
    assert result.exit_code == 2
    assert "Usage:" in result.stderr or "Missing command" in result.stderr


def test_implode_claude_basic_functionality():
    """Test basic implode claude functionality."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .claude/commands directory with sample files
        claude_commands_dir = Path(".claude/commands")
        claude_commands_dir.mkdir(parents=True)

        with open(claude_commands_dir / "fix-tests.md", "w") as f:
            f.write("Here are instructions to fix tests.")

        # Run implode claude command (defaults to commands.md)
        result = runner.invoke(app, ["implode", "claude"])

        # Check command succeeds
        assert result.exit_code == 0
        assert "Bundled claude commands into commands.md" in result.stdout

        # Check that output file was created
        assert Path("commands.md").exists()

        with open("commands.md", "r") as f:
            content = f.read()
            assert "## Fix Tests" in content


def test_implode_gemini_basic_functionality():
    """Test basic implode gemini functionality."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .gemini/commands directory with sample TOML files
        gemini_commands_dir = Path(".gemini/commands")
        gemini_commands_dir.mkdir(parents=True)

        with open(gemini_commands_dir / "fix-tests.toml", "w") as f:
            f.write('''name = "fix-tests"
description = "Fix Tests"

[command]
shell = """
Here are instructions to fix tests.
"""
''')

        # Run implode gemini command (defaults to commands.md)
        result = runner.invoke(app, ["implode", "gemini"])

        # Check command succeeds
        assert result.exit_code == 0
        assert "Bundled gemini commands into commands.md" in result.stdout

        # Check that output file was created
        assert Path("commands.md").exists()

        with open("commands.md", "r") as f:
            content = f.read()
            assert "## Fix Tests" in content
            assert "Here are instructions to fix tests." in content
