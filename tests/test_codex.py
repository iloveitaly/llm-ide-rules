"""Tests for Codex CLI agent integration."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.agents.codex import CodexAgent
from llm_ide_rules.constants import ensure_agents_adapter


def test_codex_does_not_write_rules_dir():
    agent = CodexAgent()

    assert agent.rules_dir is None


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
