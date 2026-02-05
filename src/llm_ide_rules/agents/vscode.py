"""VS Code agent implementation."""

import json
from pathlib import Path

from llm_ide_rules.agents.base import BaseAgent
from llm_ide_rules.mcp import McpServer


class VSCodeAgent(BaseAgent):
    """Agent for VS Code (native MCP support)."""

    name = "vscode"
    rules_dir = None  # VS Code typically uses .github (handled by GitHubAgent)
    commands_dir = None
    rule_extension = None
    command_extension = None

    mcp_global_path = None  # VS Code user settings are complex, focusing on workspace
    mcp_project_path = ".vscode/mcp.json"
    mcp_root_key = "servers"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """VS Code doesn't support rules directly (uses GitHub Copilot)."""
        return False

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """VS Code doesn't support commands directly."""
        return False

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        """VS Code doesn't support rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """VS Code doesn't support commands."""
        pass

    def transform_mcp_server(self, server: McpServer) -> dict:
        """Transform unified server to VS Code format."""
        # VS Code uses "env" key, similar to standard MCP
        base = {}
        if server.env:
            base["env"] = server.env

        if server.url:
            # VS Code supports SSE via "url" (or "type": "sse"?)
            # Research indicates basic MCP config in VS Code is similar to Claude
            # but usually requires "command" for stdio.
            # However, for remote/SSE, it might just need 'url'.
            # Let's assume standard 'url' for now based on 'mcp.json' schema compatibility.
            return {"url": server.url, **base}

        return {
            "command": server.command,
            "args": server.args or [],
            **base,
        }

    def reverse_transform_mcp_server(self, name: str, config: dict) -> McpServer:
        """Transform VS Code config back to unified format."""
        if "url" in config:
            return McpServer(
                url=config["url"],
                env=config.get("env"),
            )

        return McpServer(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env"),
        )
