"""OpenCode agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import BaseAgent


class OpenCodeAgent(BaseAgent):
    """Agent for OpenCode."""

    name = "opencode"
    rules_dir = None
    commands_dir = None
    rule_extension = None
    command_extension = None

    mcp_global_path = ".config/opencode/opencode.json"
    mcp_project_path = "opencode.json"
    mcp_root_key = "mcp"

    def bundle_rules(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """OpenCode doesn't support rules."""
        return False

    def bundle_commands(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """OpenCode doesn't support commands."""
        return False

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
    ) -> None:
        """OpenCode doesn't support rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """OpenCode doesn't support commands."""
        pass

    def transform_mcp_server(self, server: "McpServer") -> dict:
        """Transform unified server to OpenCode format (merged command array, environment key)."""
        from llm_ide_rules.mcp import McpServer

        if server.url:
            result = {"type": "sse", "url": server.url, "enabled": True}
            if server.env:
                result["environment"] = server.env
            return result

        result = {
            "type": "local",
            "command": [server.command] + (server.args or []),
            "enabled": True,
        }
        if server.env:
            result["environment"] = server.env
        return result

    def reverse_transform_mcp_server(self, name: str, config: dict) -> "McpServer":
        """Transform OpenCode config back to unified format."""
        from llm_ide_rules.mcp import McpServer

        if config.get("type") == "sse":
            return McpServer(
                url=config["url"],
                env=config.get("environment"),
            )

        command_array = config["command"]
        return McpServer(
            command=command_array[0] if command_array else None,
            args=command_array[1:] if len(command_array) > 1 else [],
            env=config.get("environment"),
        )
