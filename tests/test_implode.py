"""Test implode command functionality."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_implode_help():
    """Test that implode command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "--help"])
    assert result.exit_code == 0
    assert "Bundle rule files into a single instruction file" in result.stdout


def test_implode_preserves_custom_instructions():
    """Test that implode preserves custom instructions after the marker."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Pre-create output file with custom instructions
        output_file = Path("instructions.md")
        output_file.write_text(
            "Old rules\n<!-- END CLONED INSTRUCTIONS -->\nMy Custom Rules",
            encoding="utf-8",
        )

        # Create .cursor/rules directory
        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)
        (cursor_rules_dir / "python.mdc").write_text(
            "---\ndescription: Python\n---\n## Python\n\nNew remote rules",
            encoding="utf-8",
        )

        result = runner.invoke(app, ["implode", "cursor", str(output_file)])

        assert result.exit_code == 0
        content = output_file.read_text(encoding="utf-8")
        assert "New remote rules" in content
        assert "<!-- END CLONED INSTRUCTIONS -->" in content
        assert "My Custom Rules" in content
        assert "Old rules" not in content


def test_implode_does_not_accumulate_newlines_on_repeated_runs():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        output_file = Path("instructions.md")

        cursor_rules_dir = Path(".cursor/rules")
        cursor_rules_dir.mkdir(parents=True)
        (cursor_rules_dir / "python.mdc").write_text(
            "---\ndescription: Python\n---\n## Python\n\nRule content",
            encoding="utf-8",
        )

        # run implode 3 times
        for _ in range(3):
            result = runner.invoke(app, ["implode", "cursor", str(output_file)])
            assert result.exit_code == 0

        content1 = output_file.read_text(encoding="utf-8")
        assert content1.endswith("<!-- END CLONED INSTRUCTIONS -->\n")
        assert not content1.endswith("<!-- END CLONED INSTRUCTIONS -->\n\n")

        # add custom content and run 3 more times
        output_file.write_text(f"{content1}\n# My Custom Rules\n", encoding="utf-8")

        for _ in range(3):
            result = runner.invoke(app, ["implode", "cursor", str(output_file)])
            assert result.exit_code == 0

        content2 = output_file.read_text(encoding="utf-8")
        assert "<!-- END CLONED INSTRUCTIONS -->\n\n# My Custom Rules\n" in content2
        assert "<!-- END CLONED INSTRUCTIONS -->\n\n\n" not in content2


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
        with open("bundled.md") as f:
            content = f.read()
            assert "## Python" in content
            assert "## React" in content
            assert "Here are Python rules for development" in content
            assert "Here are React rules for frontend development" in content


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
        with open("bundled-github.md") as f:
            content = f.read()
            assert "## Python" in content
            assert "## React" in content
            assert "Here are Python instructions for development" in content
            assert "Here are React instructions for frontend development" in content


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

        claude_rules_dir = Path(".claude/rules")
        claude_rules_dir.mkdir(parents=True)

        with open(claude_rules_dir / "python.md", "w") as f:
            f.write("""---
paths:
  - "**/*.py"
---

## Python

Here are Python rules for development.""")

        result = runner.invoke(app, ["implode", "claude"])

        assert result.exit_code == 0
        assert "Bundled claude rules into instructions.md" in result.stdout
        assert "commands.md" not in result.stdout

        assert Path("instructions.md").exists()
        assert not Path("commands.md").exists()

        with open("instructions.md") as f:
            content = f.read()
            assert "## Python" in content
            assert "globs: **/*.py" in content
            assert "Here are Python rules for development." in content


def test_implode_opencode_basic_functionality():
    """Test implode opencode bundles AGENTS.md into instructions.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("AGENTS.md").write_text(
            """# General

## Python

Here are Python rules.
"""
        )

        result = runner.invoke(app, ["implode", "opencode"])

        assert result.exit_code == 0
        assert (
            "Bundled OpenCode rules (AGENTS.md) into instructions.md" in result.stdout
        )
        assert Path("instructions.md").exists()
        assert not Path("commands.md").exists()

        content = Path("instructions.md").read_text()
        assert "## Python" in content
        assert "Here are Python rules." in content


def test_implode_codex_basic_functionality():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("AGENTS.md").write_text("General Codex rules.\n")

        result = runner.invoke(app, ["implode", "codex"])

        assert result.exit_code == 0
        assert "Bundled Codex rules (AGENTS.md) into instructions.md" in result.stdout
        assert not Path("commands.md").exists()
        assert Path("instructions.md").exists()
        assert "General Codex rules." in Path("instructions.md").read_text()


def test_implode_codex_help():
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "codex", "--help"])
    assert result.exit_code == 0
    assert "Bundle Codex" in result.stdout


def test_implode_codex_missing_directory():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["implode", "codex", "bundled.md"])

        assert result.exit_code == 1


def test_implode_opencode_help():
    """Test that implode opencode subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["implode", "opencode", "--help"])
    assert result.exit_code == 0
    assert "Bundle OpenCode" in result.stdout


def test_implode_opencode_missing_agents_md():
    """Test implode opencode when AGENTS.md is missing."""
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

        claude_rules_dir = project_root / ".claude" / "rules"
        claude_rules_dir.mkdir(parents=True)

        with open(claude_rules_dir / "python.md", "w") as f:
            f.write("""## Python

Here are Python rules for development.""")

        os.chdir(str(project_root / ".claude"))

        result = runner.invoke(app, ["implode", "claude"])

        assert result.exit_code == 0
        assert "Bundled claude rules into instructions.md" in result.stdout

        instructions_file = project_root / "instructions.md"
        assert instructions_file.exists()
        assert not (project_root / "commands.md").exists()

        with open(instructions_file) as f:
            content = f.read()
            assert "## Python" in content
            assert "Here are Python rules for development." in content


def test_implode_claude_missing_rules_directory():
    """Test implode claude with missing .claude/rules directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["implode", "claude", "bundled.md"])

        assert result.exit_code == 1


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

        with open("bundled.md") as f:
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

        with open("bundled-github.md") as f:
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

        explode_result = runner.invoke(app, ["explode", "cursor"])
        assert explode_result.exit_code == 0

        implode_result = runner.invoke(app, ["implode", "cursor", "bundled.md"])
        assert implode_result.exit_code == 0

        with open("bundled.md") as f:
            bundled_content = f.read()
            assert "## Python" in bundled_content
            assert "globs: **/*.py" in bundled_content
            assert "## TypeScript" in bundled_content
            assert "globs: **/*.ts" in bundled_content
