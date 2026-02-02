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


def test_implode_github_help():
    """Test that implode github subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "github", "--help"])
    assert result.exit_code == 0
    assert "Bundle GitHub" in result.stdout


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


def test_implode_opencode_basic_functionality():
    """Test basic implode opencode functionality."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create .opencode/commands directory with sample files
        opencode_commands_dir = Path(".opencode/commands")
        opencode_commands_dir.mkdir(parents=True)

        with open(opencode_commands_dir / "fix-tests.md", "w") as f:
            f.write("Here are instructions to fix tests.")

        # Run implode opencode command (defaults to commands.md)
        result = runner.invoke(app, ["implode", "opencode"])

        # Check command succeeds
        assert result.exit_code == 0
        assert "Bundled opencode commands into commands.md" in result.stdout

        # Check that output file was created
        assert Path("commands.md").exists()

        with open("commands.md", "r") as f:
            content = f.read()
            assert "## Fix Tests" in content
            assert "Here are instructions to fix tests." in content


def test_implode_opencode_help():
    """Test that implode opencode subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "opencode", "--help"])
    assert result.exit_code == 0
    assert "Bundle OpenCode" in result.stdout


def test_implode_opencode_missing_directory():
    """Test implode opencode with missing .opencode/commands directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run implode opencode command without creating commands directory
        result = runner.invoke(app, ["implode", "opencode", "bundled.md"])

        # Should fail with error
        assert result.exit_code == 1


def test_implode_claude_from_subdirectory():
    """Test that implode claude works when run from within the .claude directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)

        claude_commands_dir = project_root / ".claude" / "commands"
        claude_commands_dir.mkdir(parents=True)

        with open(claude_commands_dir / "fix-tests.md", "w") as f:
            f.write("Here are instructions to fix tests.")

        os.chdir(str(project_root / ".claude"))

        result = runner.invoke(app, ["implode", "claude"])

        assert result.exit_code == 0
        assert "Bundled claude commands into commands.md" in result.stdout

        output_file = project_root / "commands.md"
        assert output_file.exists()

        with open(output_file, "r") as f:
            content = f.read()
            assert "## Fix Tests" in content
            assert "Here are instructions to fix tests." in content


def test_implode_cursor_preserves_globs():
    """Test that implode cursor preserves glob patterns from frontmatter."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)

        with open(cursor_rules_dir / "python.mdc", "w") as f:
            f.write("""---
description: Python rules
globs: "**/*.py"
alwaysApply: false
---

## Python

Here are Python rules for development.""")

        with open(cursor_rules_dir / "typescript.mdc", "w") as f:
            f.write("""---
description: TypeScript rules
globs: "**/*.ts"
alwaysApply: false
---

## TypeScript

Here are TypeScript rules for development.""")

        result = runner.invoke(app, ["implode", "cursor", "bundled.md"])

        assert result.exit_code == 0

        with open("bundled.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert 'globs: "**/*.py"' in content or "globs: **/*.py" in content
            assert "## TypeScript" in content
            assert 'globs: "**/*.ts"' in content or "globs: **/*.ts" in content


def test_implode_github_preserves_globs():
    """Test that implode github preserves applyTo patterns from frontmatter."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        github_instructions_dir = Path(".github/instructions")
        github_instructions_dir.mkdir(parents=True)

        with open(github_instructions_dir / "python.instructions.md", "w") as f:
            f.write("""---
applyTo: "**/*.py"
---

## Python

Here are Python instructions for development.""")

        with open(github_instructions_dir / "javascript.instructions.md", "w") as f:
            f.write("""---
applyTo: "**/*.js"
---

## JavaScript

Here are JavaScript instructions for development.""")

        result = runner.invoke(app, ["implode", "github", "bundled-github.md"])

        assert result.exit_code == 0

        with open("bundled-github.md", "r") as f:
            content = f.read()
            assert "## Python" in content
            assert "globs: **/*.py" in content
            assert "## Javascript" in content
            assert "globs: **/*.js" in content


def test_explode_implode_roundtrip_preserves_globs():
    """Test that globs are preserved through explode->implode roundtrip."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        original_content = """## Python

globs: **/*.py

Here are Python rules for development.

## TypeScript

globs: **/*.ts

Here are TypeScript rules for development."""

        with open("instructions.md", "w") as f:
            f.write(original_content)

        explode_result = runner.invoke(
            app, ["explode", "instructions.md", "--agent", "cursor"]
        )
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(app, ["implode", "cursor", "bundled.md"])
        assert implode_result.exit_code == 0

        with open("bundled.md", "r") as f:
            bundled_content = f.read()
            assert "## Python" in bundled_content
            assert "globs: **/*.py" in bundled_content
            assert "## TypeScript" in bundled_content
            assert "globs: **/*.ts" in bundled_content
