"""OpenCode agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    trim_content,
)


class OpenCodeAgent(BaseAgent):
    """Agent for OpenCode."""

    name = "opencode"
    rules_dir = None
    commands_dir = ".opencode/commands"
    rule_extension = None
    command_extension = ".md"

    mcp_global_path = ".config/opencode/opencode.json"
    mcp_project_path = "opencode.json"
    mcp_root_key = "mcp"

    def bundle_rules(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """OpenCode doesn't support rules."""
        return False

    def bundle_commands(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """Bundle OpenCode command files (.md) into a single output file."""
        commands_path = output_file.parent / self.commands_dir
        if not commands_path.exists():
            return False

        command_files = list(commands_path.glob(f"*{self.command_extension}"))
        if not command_files:
            return False

        ordered_commands = get_ordered_files(command_files, list(section_globs.keys()))

        content_parts: list[str] = []
        for command_file in ordered_commands:
            content = command_file.read_text().strip()
            if not content:
                continue

            header = resolve_header_from_stem(command_file.stem, section_globs)
            content_parts.append(f"## {header}\n\n")
            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        output_file.write_text("".join(content_parts))
        return True

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
        """Write an OpenCode command file (.md) - plain markdown, no frontmatter."""
        filepath = commands_dir / f"{filename}{self.command_extension}"

        trimmed = trim_content(content_lines)
        filepath.write_text("".join(trimmed))

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
