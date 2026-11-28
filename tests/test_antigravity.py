"""Tests for Antigravity CLI agent integration."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.agents.antigravity import AntigravityAgent
from llm_ide_rules.constants import ensure_agents_adapter


def test_antigravity_does_not_write_rules_dir():
    agent = AntigravityAgent()

    assert agent.rules_dir is None


def test_explode_antigravity_writes_agents_md_not_rules():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            Path("instructions.md").write_text(
                """# Sample Instructions

These are general Antigravity rules.

## Python

globs: *.py
Description: Python rule description

Here are Python rules for development.
"""
            )

            result = runner.invoke(app, ["explode", "antigravity"])

            assert result.exit_code == 0
            assert Path("AGENTS.md").exists()
            assert (
                "These are general Antigravity rules." in Path("AGENTS.md").read_text()
            )
            assert "## Python" in Path("AGENTS.md").read_text()
            assert not Path(".agents/rules").exists()
        finally:
            os.chdir(original_cwd)


def test_roundtrip_antigravity_instructions():
    """Test explode -> implode antigravity produces equivalent instructions.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            original_content = """# Sample Instructions

## Python

globs: *.py
Description: Python rule description

Here are Python rules for development.

Use Python 3.13 and prefer Pathlib.

## React

globs: manual
Description: React rule description

Here are React rules for frontend development.

Use functional components and hooks.
"""

            Path("instructions.md").write_text(original_content)

            explode_result = runner.invoke(app, ["explode", "antigravity"])
            assert explode_result.exit_code == 0

            assert Path("AGENTS.md").exists()
            assert not Path(".agents/rules").exists()

            implode_result = runner.invoke(
                app, ["implode", "antigravity", "roundtrip.md"]
            )
            assert implode_result.exit_code == 0

            roundtrip_content = Path("roundtrip.md").read_text()
            assert "## Python" in roundtrip_content
            assert "Here are Python rules for development." in roundtrip_content
            assert "Use Python 3.13 and prefer Pathlib." in roundtrip_content
            assert "## React" in roundtrip_content
            assert "Here are React rules for frontend development." in roundtrip_content
            assert "Use functional components and hooks." in roundtrip_content
        finally:
            os.chdir(original_cwd)


def test_explode_antigravity_runtime_when_disk_empty(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv("ANTIGRAVITY_AGENT", "true")

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            Path("instructions.md").write_text("## Python\n\nPython rules\n")

            result = runner.invoke(app, ["explode"])

            assert result.exit_code == 0
            assert "Detected runtime environment: antigravity" in result.stdout
            assert Path("AGENTS.md").exists()
            assert not Path(".agents/rules").exists()
            assert not Path(".cursor").exists()
        finally:
            os.chdir(original_cwd)


def test_ensure_agents_adapter_appends_for_antigravity():
    assert ensure_agents_adapter(["antigravity"]) == ["antigravity", "agents"]
    assert ensure_agents_adapter(["antigravity", "agents"]) == ["antigravity", "agents"]


def test_extract_frontmatter_description():
    """Test extracting single-line and multiline frontmatter descriptions."""
    from llm_ide_rules.agents.dotagents import extract_frontmatter_description

    # Single-line
    lines = ["---", "name: test-skill", "description: Simple description", "---"]
    assert extract_frontmatter_description(lines) == "Simple description"

    # Folded scalar >-
    lines_folded = [
        "---",
        "name: copier-sync",
        "description: >-",
        "  First line of description,",
        "  second line of description.",
        "---",
    ]
    assert (
        extract_frontmatter_description(lines_folded)
        == "First line of description, second line of description."
    )

    # Literal scalar |
    lines_literal = [
        "---",
        "name: multiline-skill",
        "description: |",
        "  Line 1",
        "  Line 2",
        "---",
    ]
    assert extract_frontmatter_description(lines_literal) == "Line 1\nLine 2"

    # Empty frontmatter
    assert extract_frontmatter_description([]) is None
    assert extract_frontmatter_description(["not frontmatter"]) is None
