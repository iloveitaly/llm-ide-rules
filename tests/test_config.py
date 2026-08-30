"""Test config command."""

import json
import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_config_github():
    """Test that the config command correctly configures GitHub / VSCode."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["config", "github"])
        assert result.exit_code == 0
        assert "Configured github" in result.stdout

        settings_path = Path(".vscode/settings.json")
        assert settings_path.exists()
        data = json.loads(settings_path.read_text())
        assert data.get("chat.useAgentsMdFile") is True
        assert data.get("chat.useNestedAgentsMdFiles") is True


def test_config_all_agents():
    """Test that the config command correctly configures all agents when none is specified."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configured github" in result.stdout
        assert Path(".vscode/settings.json").exists()
