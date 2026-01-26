"""Tests for MCP configuration management."""

import json
import os
import pytest
from pathlib import Path
from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.agents import get_agent
from llm_ide_rules.agents.claude import ClaudeAgent
from llm_ide_rules.agents.gemini import GeminiAgent
from llm_ide_rules.agents.github import GitHubAgent
from llm_ide_rules.agents.opencode import OpenCodeAgent
from llm_ide_rules.mcp import McpServer

runner = CliRunner()


@pytest.fixture(autouse=True)
def restore_cwd():
    """Ensure tests have a valid working directory."""
    try:
        original_cwd = Path.cwd()
    except (FileNotFoundError, OSError):
        original_cwd = Path.home()
        os.chdir(original_cwd)

    yield

    try:
        os.chdir(original_cwd)
    except (FileNotFoundError, OSError):
        os.chdir(Path.home())


# Unit Tests for Transform Functions


def test_transform_mcp_server_stdio_standard():
    """Test standard stdio server transform (Claude/Cursor)."""
    server = McpServer(command="npx", args=["@pkg/name"])
    agent = ClaudeAgent()
    result = agent.transform_mcp_server(server)
    assert result == {"command": "npx", "args": ["@pkg/name"]}


def test_transform_mcp_server_remote_standard():
    """Test remote server transform."""
    server = McpServer(url="https://mcp.example.com")
    agent = ClaudeAgent()
    result = agent.transform_mcp_server(server)
    assert result == {"url": "https://mcp.example.com"}


def test_transform_mcp_server_gemini_uses_httpurl():
    """Test Gemini uses httpUrl instead of url."""
    server = McpServer(url="https://mcp.example.com")
    agent = GeminiAgent()
    result = agent.transform_mcp_server(server)
    assert result == {"httpUrl": "https://mcp.example.com"}


def test_transform_mcp_server_opencode_merges_command():
    """Test OpenCode merges command and args into array."""
    server = McpServer(command="npx", args=["-y", "@pkg/name"])
    agent = OpenCodeAgent()
    result = agent.transform_mcp_server(server)
    assert result["command"] == ["npx", "-y", "@pkg/name"]
    assert result["type"] == "local"
    assert result["enabled"] is True


def test_transform_mcp_server_copilot_adds_tools():
    """Test Copilot adds type and tools fields."""
    server = McpServer(command="npx", args=["@pkg/name"])
    agent = GitHubAgent()
    result = agent.transform_mcp_server(server)
    assert result["type"] == "local"
    assert result["tools"] == ["*"]


def test_transform_mcp_server_with_env():
    """Test env variables are preserved."""
    server = McpServer(command="npx", args=[], env={"API_KEY": "secret"})
    agent = ClaudeAgent()
    result = agent.transform_mcp_server(server)
    assert result["env"] == {"API_KEY": "secret"}


def test_transform_mcp_server_opencode_uses_environment_key():
    """Test OpenCode uses 'environment' instead of 'env'."""
    server = McpServer(command="npx", args=[], env={"API_KEY": "secret"})
    agent = OpenCodeAgent()
    result = agent.transform_mcp_server(server)
    assert result["environment"] == {"API_KEY": "secret"}
    assert "env" not in result


# Reverse Transform Tests


def test_reverse_transform_mcp_server_stdio():
    """Test reverse transform from platform to unified format."""
    agent = ClaudeAgent()
    config = {"command": "npx", "args": ["-y", "@pkg/name"]}
    result = agent.reverse_transform_mcp_server("test", config)
    assert result.command == "npx"
    assert result.args == ["-y", "@pkg/name"]


def test_reverse_transform_mcp_server_opencode_splits_command():
    """Test OpenCode reverse transform splits merged command array."""
    agent = OpenCodeAgent()
    config = {"type": "local", "command": ["npx", "-y", "@pkg/name"], "enabled": True}
    result = agent.reverse_transform_mcp_server("test", config)
    assert result.command == "npx"
    assert result.args == ["-y", "@pkg/name"]


def test_reverse_transform_mcp_server_gemini_httpurl():
    """Test Gemini reverse transform handles httpUrl."""
    agent = GeminiAgent()
    config = {"httpUrl": "https://mcp.example.com"}
    result = agent.reverse_transform_mcp_server("test", config)
    assert result.url == "https://mcp.example.com"


def test_reverse_transform_mcp_server_github_http():
    """Test GitHub reverse transform handles http type."""
    agent = GitHubAgent()
    config = {"type": "http", "url": "https://mcp.example.com", "tools": ["*"]}
    result = agent.reverse_transform_mcp_server("test", config)
    assert result.url == "https://mcp.example.com"


# CLI Integration Tests


def test_mcp_explode_help():
    """Test mcp explode command shows help."""
    result = runner.invoke(app, ["mcp", "explode", "--help"])
    assert result.exit_code == 0
    assert "Convert unified mcp.json" in result.stdout


def test_mcp_explode_basic(tmp_path, monkeypatch):
    """Test basic explode creates platform configs."""
    monkeypatch.chdir(tmp_path)

    mcp_json = {"servers": {"test": {"command": "npx", "args": ["-y", "@pkg/name"]}}}
    (tmp_path / "mcp.json").write_text(json.dumps(mcp_json))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json"])

    assert result.exit_code == 0
    assert (tmp_path / ".mcp.json").exists()
    assert (tmp_path / ".cursor/mcp.json").exists()
    assert (tmp_path / "opencode.json").exists()


def test_mcp_explode_remote_server(tmp_path, monkeypatch):
    """Test explode handles remote/SSE servers."""
    monkeypatch.chdir(tmp_path)

    mcp_json = {"servers": {"remote": {"url": "https://mcp.example.com"}}}
    (tmp_path / "mcp.json").write_text(json.dumps(mcp_json))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json"])

    assert result.exit_code == 0

    gemini_config = json.loads((tmp_path / ".gemini/settings.json").read_text())
    assert gemini_config["mcpServers"]["remote"]["httpUrl"] == "https://mcp.example.com"


def test_mcp_explode_with_json_comments(tmp_path, monkeypatch):
    """Test explode handles JSON with // comments via json5."""
    monkeypatch.chdir(tmp_path)

    mcp_content = """{"servers": {"test": {"command": "npx", "args": ["@pkg/name"]}}}"""
    (tmp_path / "mcp.json").write_text(mcp_content)

    result = runner.invoke(app, ["mcp", "explode", "mcp.json"])
    assert result.exit_code == 0


def test_mcp_implode_basic(tmp_path, monkeypatch):
    """Test implode reads existing configs."""
    monkeypatch.chdir(tmp_path)

    claude_config = {
        "mcpServers": {"test": {"command": "npx", "args": ["-y", "@pkg/name"]}}
    }
    (tmp_path / ".mcp.json").write_text(json.dumps(claude_config))

    result = runner.invoke(app, ["mcp", "implode", "output.json", "--source", "claude"])

    assert result.exit_code == 0
    output = json.loads((tmp_path / "output.json").read_text())
    assert "test" in output["servers"]


def test_mcp_explode_scope_global(tmp_path, monkeypatch, mocker):
    """Test explode with --scope global writes to home directory."""
    monkeypatch.chdir(tmp_path)
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    mocker.patch("pathlib.Path.home", return_value=mock_home)

    mcp_json = {"servers": {"test": {"command": "npx", "args": []}}}
    (tmp_path / "mcp.json").write_text(json.dumps(mcp_json))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json", "--scope", "global"])

    assert result.exit_code == 0
    assert (mock_home / ".claude.json").exists()


def test_mcp_explode_specific_agent(tmp_path, monkeypatch):
    """Test explode with specific agent only."""
    monkeypatch.chdir(tmp_path)

    mcp_json = {"servers": {"test": {"command": "npx", "args": []}}}
    (tmp_path / "mcp.json").write_text(json.dumps(mcp_json))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json", "--agent", "claude"])

    assert result.exit_code == 0
    assert (tmp_path / ".mcp.json").exists()
    assert not (tmp_path / ".cursor/mcp.json").exists()


def test_mcp_explode_with_env(tmp_path, monkeypatch):
    """Test explode preserves environment variables."""
    monkeypatch.chdir(tmp_path)

    mcp_json = {
        "servers": {
            "test": {
                "command": "npx",
                "args": ["@pkg/name"],
                "env": {"API_KEY": "secret"},
            }
        }
    }
    (tmp_path / "mcp.json").write_text(json.dumps(mcp_json))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json"])

    assert result.exit_code == 0

    claude_config = json.loads((tmp_path / ".mcp.json").read_text())
    assert claude_config["mcpServers"]["test"]["env"]["API_KEY"] == "secret"

    opencode_config = json.loads((tmp_path / "opencode.json").read_text())
    assert opencode_config["mcp"]["test"]["environment"]["API_KEY"] == "secret"


def test_mcp_implode_missing_source(tmp_path, monkeypatch):
    """Test implode fails when source is not specified."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["mcp", "implode", "output.json"])
    assert result.exit_code == 1


def test_mcp_implode_missing_config(tmp_path, monkeypatch):
    """Test implode fails when source config doesn't exist."""
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["mcp", "implode", "output.json", "--source", "claude"])
    assert result.exit_code == 1


def test_gemini_write_mcp_config_merges_existing(tmp_path):
    """Test Gemini write_mcp_config merges with existing settings."""
    agent = GeminiAgent()
    settings_path = tmp_path / ".gemini/settings.json"
    settings_path.parent.mkdir(parents=True)

    existing = {"otherSetting": "value", "anotherKey": 123}
    settings_path.write_text(json.dumps(existing))

    servers = {"test": {"command": "npx", "args": []}}
    agent.write_mcp_config(servers, settings_path)

    result = json.loads(settings_path.read_text())
    assert result["mcpServers"] == servers
    assert result["otherSetting"] == "value"
    assert result["anotherKey"] == 123


def test_mcp_roundtrip(tmp_path, monkeypatch):
    """Test full roundtrip: explode then implode preserves data."""
    monkeypatch.chdir(tmp_path)

    original = {
        "servers": {
            "stdio": {"command": "npx", "args": ["-y", "@pkg/name"]},
            "remote": {"url": "https://mcp.example.com"},
            "with_env": {
                "command": "node",
                "args": ["server.js"],
                "env": {"API_KEY": "secret"},
            },
        }
    }
    (tmp_path / "mcp.json").write_text(json.dumps(original))

    result = runner.invoke(app, ["mcp", "explode", "mcp.json", "--agent", "claude"])
    assert result.exit_code == 0

    result = runner.invoke(
        app, ["mcp", "implode", "roundtrip.json", "--source", "claude"]
    )
    assert result.exit_code == 0

    roundtrip = json.loads((tmp_path / "roundtrip.json").read_text())
    assert roundtrip == original
