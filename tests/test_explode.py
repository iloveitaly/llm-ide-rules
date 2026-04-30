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
globs: *.py

Here are Python rules for development.

## React
globs: *.tsx

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
        assert "alwaysApply: false" in content
        assert "globs: *.py" in content
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

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "cursor"])

        assert result.exit_code == 0

        assert Path(".cursor/rules/python.mdc").exists()

        assert Path(".cursor/commands/fix-tests.md").exists()
        assert Path(".cursor/commands/plan-only.md").exists()

        # Other agents should not have been created because we specified --agent cursor
        assert not Path(".claude/commands/fix-tests.md").exists()
        assert not Path(".gemini/commands/fix-tests.toml").exists()
        assert not Path(".github/prompts/fix-tests.prompt.md").exists()


def test_explode_generates_general_mdc_when_agents_enabled():
    """Test that general.mdc is NOT skipped when agents agent is active."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# General Instructions

These are general rules for the project.

## Python
globs: *.py

Python specific rules.
"""
        Path("instructions.md").write_text(instructions_content)

        # Scenario A: cursor only - general.mdc SHOULD exist
        result_cursor = runner.invoke(
            app, ["explode", "instructions.md", "--agent", "cursor"]
        )
        assert result_cursor.exit_code == 0
        assert Path(".cursor/rules/general.mdc").exists()

        # Clean up for next run
        import shutil

        shutil.rmtree(".cursor")

        # Scenario B: all agents - general.mdc SHOULD ALSO exist
        result_all = runner.invoke(
            app, ["explode", "instructions.md", "--agent", "all"]
        )
        assert result_all.exit_code == 0
        assert Path(".cursor/rules/general.mdc").exists()
        assert Path("AGENTS.md").exists()
        assert (
            "These are general rules for the project" in Path("AGENTS.md").read_text()
        )


def test_explode_unmapped_section_as_always_apply():
    """Test that unmapped sections in instructions.md are treated as always-apply rules."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: *.py

Here are Python rules for development.

## Custom Unmapped Section

This section is not in sections.json so it should be treated as always-apply.
"""
        Path("instructions.md").write_text(instructions_content)

        # Scenario A: cursor only - custom-unmapped-section.mdc SHOULD exist
        result_cursor = runner.invoke(
            app, ["explode", "instructions.md", "--agent", "cursor"]
        )
        assert result_cursor.exit_code == 0
        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()
        cursor_content = Path(".cursor/rules/custom-unmapped-section.mdc").read_text()
        assert "alwaysApply: true" in cursor_content
        assert "globs: " in cursor_content

        # Clean up
        import shutil

        shutil.rmtree(".cursor")

        # Scenario B: all agents - custom-unmapped-section.mdc SHOULD NOT exist
        result_all = runner.invoke(
            app, ["explode", "instructions.md", "--agent", "all"]
        )

        assert result_all.exit_code == 0

        # MDC should NOT exist because it's representable by AGENTS.md
        assert not Path(".cursor/rules/custom-unmapped-section.mdc").exists()

        # AGENTS.md SHOULD exist and contain the content
        assert Path("AGENTS.md").exists()
        agents_content = Path("AGENTS.md").read_text()
        assert "Custom Unmapped Section" in agents_content
        assert "This section is not in sections.json" in agents_content


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

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "cursor"])

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


def test_explode_claude_rules_are_generated_with_paths_frontmatter():
    """Test that Claude rules are generated with paths frontmatter."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create the subdirectory that the glob pattern will resolve to
        Path("web").mkdir()

        instructions_content = """# Sample Instructions

## TypeScript
globs: web/**/*.ts

Here are TypeScript rules for the web directory.

## Python

Here are Python rules for the root.
"""
        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md"])

        assert result.exit_code == 0

        assert Path(".claude/rules/typescript.md").exists()
        assert Path(".claude/rules/python.md").exists()

        typescript_rule = Path(".claude/rules/typescript.md").read_text()
        assert "paths:" in typescript_rule
        assert '  - "web/**/*.ts"' in typescript_rule
        assert "## TypeScript" in typescript_rule

        python_rule = Path(".claude/rules/python.md").read_text()
        assert "paths:" not in python_rule
        assert "## Python" in python_rule

        assert Path("web/AGENTS.md").exists()


def test_explode_generates_claude_rules_without_claude_md():
    """Test that explode generates Claude rules instead of CLAUDE.md."""
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

        assert not Path("CLAUDE.md").exists()
        assert Path(".claude/rules/python.md").exists()
        assert Path(".claude/rules/unmapped.md").exists()

        # Check GEMINI.md
        gemini_md = Path("GEMINI.md")
        assert not gemini_md.exists()

        # Check AGENTS.md
        agents_md = Path("AGENTS.md")
        assert Path("AGENTS.md").exists()
        agents_content = agents_md.read_text()
        assert "## Python" in agents_content
        assert "Here are Python rules." in agents_content
        assert "## Unmapped" in agents_content
        assert "Here are unmapped rules." in agents_content


def test_explode_ignores_marker():
    """Test that explode ignores the custom instructions marker and everything after it."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        instructions_content = """# Sample Instructions

## Python
globs: *.py

Here are Python rules.

<!-- END CLONED INSTRUCTIONS -->

## Custom Local Section
This should be ignored.
"""
        Path("instructions.md").write_text(instructions_content)

        commands_content = """## Remote Command
This is a remote command.

<!-- END CLONED INSTRUCTIONS -->

## Local Command
This should be ignored.
"""
        Path("commands.md").write_text(commands_content)

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "cursor"])

        assert result.exit_code == 0

        # Verify rule from instructions.md
        assert Path(".cursor/rules/python.mdc").exists()
        python_content = Path(".cursor/rules/python.mdc").read_text()
        assert "Here are Python rules." in python_content
        assert "Custom Local Section" not in python_content
        assert "This should be ignored." not in python_content

        # Verify command from commands.md
        assert Path(".cursor/commands/remote-command.md").exists()
        assert not Path(".cursor/commands/local-command.md").exists()
        remote_command_content = Path(".cursor/commands/remote-command.md").read_text()
        assert "This is a remote command." in remote_command_content
        assert "Local Command" not in remote_command_content
