"""Test explode command functionality."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from llm_ide_rules import app


def test_explode_help():
    """Test that explode command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["explode", "--help"])
    assert result.exit_code == 0
    assert "Convert instruction file to separate rule files" in result.stdout
    assert "Agents to explode for" in result.stdout
    # Rich splits "--input" with ANSI codes in CI; match the flag name instead
    assert "input" in result.stdout


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

        result = runner.invoke(app, ["explode"])

        assert result.exit_code == 0
        assert "Created" in result.stdout
        assert "rules" in result.stdout

        assert Path(".cursor/rules").exists()
        assert not Path(".cursor/commands").exists()
        assert Path(".github/instructions").exists()
        assert not Path(".github/prompts").exists()
        assert not Path(".claude/commands").exists()

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

        result = runner.invoke(app, ["explode", "cursor"])

        assert result.exit_code == 0

        assert Path(".cursor/rules/python.mdc").exists()

        assert Path(".cursor/commands/fix-tests.md").exists()
        assert Path(".cursor/commands/plan-only.md").exists()

        # Other agents should not have been created because we specified cursor
        assert not Path(".claude/commands/fix-tests.md").exists()
        assert not Path(".github/prompts/fix-tests.prompt.md").exists()


def test_explode_commands_without_description_omits_frontmatter_description():
    """Test explode with commands with and without explicit Description: line."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text("## General\nGeneral instructions\n")
        Path("commands.md").write_text(
            """## With Desc

Description: Explicit description

Instructions with description.

## No Desc

Instructions without explicit description.
"""
        )

        result = runner.invoke(app, ["explode", "antigravity", "claude", "opencode", "github"])
        assert result.exit_code == 0

        # Antigravity (.agents/skills)
        ag_with = Path(".agents/skills/with-desc/SKILL.md").read_text()
        assert "name: with-desc" in ag_with
        assert "description: Explicit description" in ag_with

        ag_no = Path(".agents/skills/no-desc/SKILL.md").read_text()
        assert "name: no-desc" in ag_no
        assert "description:" not in ag_no

        # Claude (.claude/commands)
        claude_with = Path(".claude/commands/with-desc.md").read_text()
        assert "description: Explicit description" in claude_with

        claude_no = Path(".claude/commands/no-desc.md").read_text()
        assert "---" not in claude_no
        assert "description:" not in claude_no
        assert "Instructions without explicit description." in claude_no

        # OpenCode (.opencode/commands)
        opencode_with = Path(".opencode/commands/with-desc.md").read_text()
        assert "description: Explicit description" in opencode_with

        opencode_no = Path(".opencode/commands/no-desc.md").read_text()
        assert "---" not in opencode_no
        assert "description:" not in opencode_no

        # GitHub (.github/prompts)
        gh_with = Path(".github/prompts/with-desc.prompt.md").read_text()
        assert "mode: 'agent'" in gh_with
        assert "description: 'Explicit description'" in gh_with

        gh_no = Path(".github/prompts/no-desc.prompt.md").read_text()
        assert "mode: 'agent'" in gh_no
        assert "description:" not in gh_no


def test_explode_space_separated_agents():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text(
            """# Sample Instructions

## Python
globs: *.py

Here are Python rules for development.
"""
        )

        result = runner.invoke(app, ["explode", "cursor", "claude"])

        assert result.exit_code == 0
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".claude/rules/python.md").exists()
        assert not Path(".github/instructions").exists()


def test_explode_from_exploded_output():
    runner = CliRunner()

    with (
        tempfile.TemporaryDirectory() as source_dir,
        tempfile.TemporaryDirectory() as dest_dir,
    ):
        Path(source_dir, ".cursor").mkdir()
        Path(source_dir, ".claude").mkdir()

        os.chdir(dest_dir)
        Path("instructions.md").write_text(
            """# Sample Instructions

## Python
globs: *.py

Here are Python rules for development.
"""
        )

        exploded = runner.invoke(app, ["exploded", source_dir])
        assert exploded.exit_code == 0

        # same split `$(llm-ide-rules exploded ...)` uses
        result = runner.invoke(app, ["explode", *exploded.stdout.split()])

        assert result.exit_code == 0
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".claude/rules/python.md").exists()
        assert not Path(".github/instructions").exists()


def test_explode_custom_input_file():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("custom.md").write_text(
            """# Sample Instructions

## Python
globs: *.py

Here are Python rules for development.
"""
        )

        result = runner.invoke(app, ["explode", "cursor", "--input", "custom.md"])

        assert result.exit_code == 0
        assert Path(".cursor/rules/python.mdc").exists()
        assert not Path(".claude/rules").exists()


def test_explode_invalid_agent():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text("# Sample Instructions\n")

        result = runner.invoke(app, ["explode", "cursor", "nope"])

        assert result.exit_code == 1
        assert "Invalid agent 'nope'" in result.stderr
        assert not Path(".cursor").exists()


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
        result_cursor = runner.invoke(app, ["explode", "cursor"])
        assert result_cursor.exit_code == 0
        assert Path(".cursor/rules/general.mdc").exists()

        shutil.rmtree(".cursor")

        # Scenario B: all agents - general.mdc SHOULD ALSO exist
        result_all = runner.invoke(app, ["explode", "all"])
        assert result_all.exit_code == 0
        assert Path(".cursor/rules/general.mdc").exists()
        assert Path(".claude/rules/general.md").exists()
        assert Path(".agents/rules/general.md").exists()
        assert Path(".github/copilot-instructions.md").exists()
        assert not Path(".github/instructions/general.instructions.md").exists()
        assert Path("AGENTS.md").exists()
        assert (
            "These are general rules for the project" in Path("AGENTS.md").read_text()
        )
        agents_general = Path(".agents/rules/general.md").read_text()
        assert "alwaysApply: true" in agents_general
        assert "These are general rules for the project" in agents_general


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
        result_cursor = runner.invoke(app, ["explode", "cursor"])
        assert result_cursor.exit_code == 0
        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()
        cursor_content = Path(".cursor/rules/custom-unmapped-section.mdc").read_text()
        assert "alwaysApply: true" in cursor_content
        assert "globs: " in cursor_content

        shutil.rmtree(".cursor")

        # Scenario B: all agents - custom-unmapped-section.mdc SHOULD exist
        result_all = runner.invoke(app, ["explode", "all"])

        assert result_all.exit_code == 0

        # MDC should exist even if AGENTS.md is also generated
        assert Path(".cursor/rules/custom-unmapped-section.mdc").exists()
        assert Path(".agents/rules/custom-unmapped-section.md").exists()
        agents_unmapped = Path(".agents/rules/custom-unmapped-section.md").read_text()
        assert "alwaysApply: true" in agents_unmapped
        assert "globs: []" in agents_unmapped

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

        result = runner.invoke(app, ["explode"])

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

This should be parsed as a glob (flexible parsing).

## ExtraWhitespace
globs:   **/*.whitespace

This should work with extra whitespace after colon.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "cursor"])

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
        assert "alwaysApply: false" in nospace_content
        assert "description: NoSpace" in nospace_content
        assert "**/*.nospace" in nospace_content
        assert "globs:**/*.nospace" not in nospace_content

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

        result = runner.invoke(app, ["explode", "--input", "nonexistent.md"])

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

        result = runner.invoke(app, ["explode"])

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

        result = runner.invoke(app, ["explode"])

        assert result.exit_code == 0

        assert not Path("CLAUDE.md").exists()
        assert Path(".claude/rules/python.md").exists()
        assert Path(".claude/rules/unmapped.md").exists()

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

        result = runner.invoke(app, ["explode", "cursor"])

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


def test_explode_infers_already_exploded_agents():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".cursor").mkdir()
        Path("instructions.md").write_text("## Python\n\nPython rules\n")

        result = runner.invoke(app, ["explode"])

        assert result.exit_code == 0
        assert "Detected active agents: cursor" in result.stdout
        assert Path(".cursor/rules/python.mdc").exists()
        assert not Path(".github").exists()
        assert not Path(".claude").exists()


def test_explode_disk_wins_over_cursor_cloud(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", "bc-test-id")

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path(".claude").mkdir()
        Path("instructions.md").write_text("## Python\n\nPython rules\n")

        result = runner.invoke(app, ["explode"])

        assert result.exit_code == 0
        assert "Detected active agents: claude" in result.stdout
        assert Path(".claude/rules/python.md").exists()
        assert not Path(".cursor").exists()
        assert not Path(".github").exists()


def test_explode_cursor_cloud_when_disk_empty(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", "bc-test-id")

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text("## Python\n\nPython rules\n")

        result = runner.invoke(app, ["explode"])

        assert result.exit_code == 0
        assert "Detected runtime environment: cursor" in result.stdout
        assert Path(".cursor/rules/python.mdc").exists()
        assert not Path(".claude").exists()
        assert not Path(".github").exists()


def test_explode_explicit_all_overrides_cursor_cloud(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", "bc-test-id")

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text("## Python\n\nPython rules\n")

        result = runner.invoke(app, ["explode", "all"])

        assert result.exit_code == 0
        assert "Detected runtime environment" not in result.stdout
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".github/instructions/python.instructions.md").exists()


@pytest.mark.parametrize("agent_name", ["grok"])
def test_explode_dotagents_general_and_unglobbed_rules(agent_name):
    """Preamble and unglobbed H2 sections always-apply for .agents/rules clients."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text(
            """# Sample Instructions

These are standing project rules.

## Python
globs: *.py

Here are Python rules for development.

## Always On

This named section has no glob, so it always applies.
"""
        )

        result = runner.invoke(app, ["explode", agent_name])

        assert result.exit_code == 0
        assert not Path("AGENTS.md").exists()

        general_path = Path(".agents/rules/general.md")
        assert general_path.exists()
        general_content = general_path.read_text()
        assert "alwaysApply: true" in general_content
        assert "globs: []" in general_content
        assert "These are standing project rules." in general_content

        unglobbed_path = Path(".agents/rules/always-on.md")
        assert unglobbed_path.exists()
        unglobbed_content = unglobbed_path.read_text()
        assert "alwaysApply: true" in unglobbed_content
        assert "globs: []" in unglobbed_content
        assert (
            "This named section has no glob, so it always applies." in unglobbed_content
        )

        globbed_path = Path(".agents/rules/python.md")
        assert globbed_path.exists()
        globbed_content = globbed_path.read_text()
        assert "alwaysApply: false" in globbed_content
        assert 'globs: ["*.py"]' in globbed_content


@pytest.mark.parametrize("agent_name", ["grok"])
def test_roundtrip_dotagents_preserves_preamble(agent_name):
    """Explode then implode keeps preamble text for grok."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text(
            """These are standing project rules.

## Python
globs: *.py

Here are Python rules for development.
"""
        )

        explode_result = runner.invoke(app, ["explode", agent_name])
        assert explode_result.exit_code == 0
        assert Path(".agents/rules/general.md").exists()

        implode_result = runner.invoke(app, ["implode", agent_name, "roundtrip.md"])
        assert implode_result.exit_code == 0

        roundtrip = Path("roundtrip.md").read_text()
        assert "These are standing project rules." in roundtrip
        assert "## Python" in roundtrip
        assert "globs: *.py" in roundtrip


def test_explode_github_preamble_stays_in_copilot_instructions():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("instructions.md").write_text(
            """These are standing project rules.

## Python
globs: *.py

Here are Python rules for development.
"""
        )

        result = runner.invoke(app, ["explode", "github"])

        assert result.exit_code == 0
        assert Path(".github/copilot-instructions.md").exists()
        assert (
            "These are standing project rules."
            in Path(".github/copilot-instructions.md").read_text()
        )
        assert not Path(".github/instructions/general.instructions.md").exists()
