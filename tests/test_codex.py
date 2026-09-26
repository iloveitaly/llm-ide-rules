"""Tests for Codex CLI agent integration."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.agents.codex import CodexAgent
from llm_ide_rules.constants import ensure_agents_adapter


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    lines = text.strip().split("\n")
    normalized_lines = [line.rstrip() for line in lines]
    while normalized_lines and not normalized_lines[-1]:
        normalized_lines.pop()
    return "\n".join(normalized_lines)


def extract_sections(text: str) -> dict[str, str]:
    """Extract sections from markdown text for easier comparison."""
    marker = "<!-- END CLONED INSTRUCTIONS -->"
    if marker in text:
        text = text.split(marker, 1)[0]

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


def test_codex_does_not_write_rules_dir():
    agent = CodexAgent()

    assert agent.rules_dir is None
    assert agent.commands_dir == ".agents/skills"


def test_codex_write_command():
    agent = CodexAgent()
    with tempfile.TemporaryDirectory() as temp_dir:
        commands_dir = Path(temp_dir) / ".agents/skills"

        agent.write_command(
            content_lines=[
                "## Deploy App\n",
                "Description: How to deploy\n",
                "\n",
                "Run fab deploy.\n",
            ],
            filename="deploy-app",
            commands_dir=commands_dir,
            section_name="Deploy App",
        )

        skill_file = commands_dir / "deploy-app/SKILL.md"
        assert skill_file.exists()
        content = skill_file.read_text()
        assert "name: deploy-app" in content
        assert "description: How to deploy" in content
        assert "# Deploy App" in content
        assert "Run fab deploy." in content


def test_codex_write_command_without_description():
    """Test that CodexAgent omits description in frontmatter when not provided."""
    agent = CodexAgent()
    with tempfile.TemporaryDirectory() as temp_dir:
        commands_dir = Path(temp_dir) / ".agents/skills"

        agent.write_command(
            content_lines=[
                "## Deploy App\n",
                "\n",
                "Run fab deploy.\n",
            ],
            filename="deploy-app",
            commands_dir=commands_dir,
            section_name="Deploy App",
        )

        skill_file = commands_dir / "deploy-app/SKILL.md"
        assert skill_file.exists()
        content = skill_file.read_text()
        assert "name: deploy-app" in content
        assert "description:" not in content
        assert "# Deploy App" in content
        assert "Run fab deploy." in content


def test_explode_codex_writes_agents_md_not_rules():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            Path("instructions.md").write_text(
                """# Sample Instructions

These are general Codex rules.

## Python

globs: *.py
Description: Python rule description

Here are Python rules for development.
"""
            )

            result = runner.invoke(app, ["explode", "codex"])

            assert result.exit_code == 0
            assert Path("AGENTS.md").exists()
            assert "These are general Codex rules." in Path("AGENTS.md").read_text()
            assert "## Python" in Path("AGENTS.md").read_text()
            assert not Path(".agents/rules").exists()
        finally:
            os.chdir(original_cwd)


def test_roundtrip_codex_instructions():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            original_content = """# Sample Instructions

These are general Codex rules.

## Python

globs: *.py
Description: Python rule description

Here are Python rules for development.

Use Python 3.13 and prefer Pathlib.
"""
            Path("instructions.md").write_text(original_content)

            explode_result = runner.invoke(app, ["explode", "codex"])
            assert explode_result.exit_code == 0
            assert Path("AGENTS.md").exists()
            assert not Path(".agents/rules").exists()

            implode_result = runner.invoke(app, ["implode", "codex"])
            assert implode_result.exit_code == 0

            roundtrip_content = Path("instructions.md").read_text()
            assert "These are general Codex rules." in roundtrip_content
            assert "## Python" in roundtrip_content
            assert "Here are Python rules for development." in roundtrip_content
        finally:
            os.chdir(original_cwd)


def test_roundtrip_codex_commands():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            Path("instructions.md").write_text(
                """# Sample Instructions

## Python

Python rules.
"""
            )
            commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix any errors that occur.

## Plan Only

Description: Plan without executing

Create a plan for the implementation.
"""
            Path("commands.md").write_text(commands_content)

            explode_result = runner.invoke(app, ["explode", "codex"])
            assert explode_result.exit_code == 0

            assert Path(".agents/skills/fix-tests/SKILL.md").exists()
            assert Path(".agents/skills/plan-only/SKILL.md").exists()
            assert not Path(".agents/rules").exists()

            implode_result = runner.invoke(app, ["implode", "codex"])
            assert implode_result.exit_code == 0

            roundtrip_content = Path("commands.md").read_text()
            original_sections = extract_sections(commands_content)
            roundtrip_sections = extract_sections(roundtrip_content)

            assert set(original_sections.keys()) == set(roundtrip_sections.keys())

            for section_name in original_sections:
                assert normalize_whitespace(
                    original_sections[section_name]
                ) == normalize_whitespace(roundtrip_sections[section_name])
        finally:
            os.chdir(original_cwd)


def test_explode_codex_runtime_when_disk_empty(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("CODEX_THREAD_ID", "thread-1")

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            Path("instructions.md").write_text("## Python\n\nPython rules\n")

            result = runner.invoke(app, ["explode"])

            assert result.exit_code == 0
            assert "Detected runtime environment: codex" in result.stdout
            assert Path("AGENTS.md").exists()
            assert not Path(".agents/rules").exists()
            assert not Path(".cursor").exists()
        finally:
            os.chdir(original_cwd)


def test_ensure_agents_adapter_appends_for_codex():
    assert ensure_agents_adapter(["codex"]) == ["codex", "agents"]
    assert ensure_agents_adapter(["codex", "agents"]) == ["codex", "agents"]
    assert ensure_agents_adapter(["cursor"]) == ["cursor"]
    assert ensure_agents_adapter(["opencode"]) == ["opencode", "agents"]
