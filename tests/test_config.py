"""Test config command and configuration warnings."""

import os
import tempfile
import json
from pathlib import Path
from typer.testing import CliRunner
from llm_ide_rules import app


from unittest.mock import patch


def test_gemini_config_warning_in_explode():
    """Test that the Gemini configuration warning is shown when config is missing during explode."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Mock expanduser to point to a non-existent directory to avoid using real global config
        with patch("os.path.expanduser", return_value=temp_dir + "/nonexistent"):
            instructions_content = "## Python\nRules here."
            Path("instructions.md").write_text(instructions_content)

            result = runner.invoke(app, ["explode", "instructions.md"])

            assert (
                "Warning: Gemini CLI configuration missing for AGENTS.md." in result.stdout
            )
            assert "llm-ide-rules config" in result.stdout
            assert "gemini config set" not in result.stdout


def test_gemini_config_warning_not_shown_when_present():
    """Test that the Gemini configuration warning is NOT shown when config is present."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Setup gemini config
        gemini_dir = Path(".gemini")
        gemini_dir.mkdir()
        (gemini_dir / "settings.json").write_text(
            '{"context": {"fileName": ["AGENTS.md"]}}'
        )

        # Mock expanduser to avoid using real global config
        with patch("os.path.expanduser", return_value=temp_dir + "/nonexistent"):
            instructions_content = "## Python\nRules here."
            Path("instructions.md").write_text(instructions_content)

            result = runner.invoke(app, ["explode", "instructions.md"])

            assert (
                "Warning: Gemini CLI configuration missing for AGENTS.md."
                not in result.stdout
            )


def test_config_gemini():
    """Test that the config command correctly configures Gemini."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Test 1: File doesn't exist
        result = runner.invoke(app, ["config", "gemini"])
        assert result.exit_code == 0
        assert "Configured gemini" in result.stdout

        settings_path = Path(".gemini/settings.json")
        assert settings_path.exists()
        data = json.loads(settings_path.read_text())
        assert "AGENTS.md" in data.get("context", {}).get("fileName", [])

        # Test 2: File exists but missing key
        settings_path.write_text('{"other": "value"}')
        result = runner.invoke(app, ["config", "gemini"])
        assert result.exit_code == 0
        assert "Configured gemini" in result.stdout

        data = json.loads(settings_path.read_text())
        assert "AGENTS.md" in data.get("context", {}).get("fileName", [])
        assert data.get("other") == "value"

        # Test 3: Already configured
        result = runner.invoke(app, ["config", "gemini"])
        assert result.exit_code == 0
        assert "Skipped gemini" in result.stdout


def test_config_all_agents():
    """Test that the config command correctly configures all agents when none is specified."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configured gemini" in result.stdout
        # Add checks for other agents if applicable, but gemini is a safe bet
        assert Path(".gemini/settings.json").exists()
