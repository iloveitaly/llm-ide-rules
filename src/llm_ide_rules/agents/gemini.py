"""Gemini CLI agent implementation."""

import json
from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_toml_metadata,
    trim_content,
    extract_description_and_filter_content,
)
from llm_ide_rules.mcp import McpServer


class GeminiAgent(BaseAgent):
    """Agent for Gemini CLI."""

    name = "gemini"
    rules_dir = None
    commands_dir = ".gemini/commands"
    rule_extension = None
    command_extension = ".toml"

    mcp_global_path = ".gemini/settings.json"
    mcp_project_path = ".gemini/settings.json"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Gemini CLI doesn't support rules, only commands."""
        return False

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Gemini CLI command files (.toml) into a single output file."""
        commands_dir = self.commands_dir
        if not commands_dir:
            return False

        commands_path = output_file.parent / commands_dir
        if not commands_path.exists():
            return False

        extension = self.command_extension
        if not extension:
            return False

        command_files = list(commands_path.glob(f"*{extension}"))
        if not command_files:
            return False

        ordered_commands = get_ordered_files(
            command_files, list(section_globs.keys()) if section_globs else None
        )

        content_parts: list[str] = []
        for command_file in ordered_commands:
            content = command_file.read_text().strip()
            if not content:
                continue

            content = strip_toml_metadata(content)
            header = resolve_header_from_stem(
                command_file.stem, section_globs if section_globs else {}
            )
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
        """Gemini CLI doesn't support rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Gemini CLI command file (.toml) with TOML format."""
        import tomli_w

        extension = self.command_extension or ".toml"
        filepath = commands_dir / f"{filename}{extension}"

        description, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )

        final_content = []
        found_header = False
        for line in filtered_content:
            if not found_header and line.startswith("## "):
                found_header = True
                continue
            final_content.append(line)

        final_content = trim_content(final_content)
        content_str = "".join(final_content).strip()

        desc = description if description else (section_name or filename)

        # Construct dict and dump to TOML
        data = {
            "description": desc,
            "prompt": content_str + "\n",  # Ensure trailing newline in multiline string
        }

        # tomli-w will handle escaping and multiline strings automatically
        output = tomli_w.dumps(data)
        filepath.write_text(output)

    def transform_mcp_server(self, server: McpServer) -> dict:
        """Transform unified server to Gemini format (uses httpUrl instead of url)."""
        if server.url:
            result: dict = {"httpUrl": server.url}
            if server.env:
                result["env"] = server.env
            return result

        result: dict = {"command": server.command, "args": server.args or []}
        if server.env:
            result["env"] = server.env
        return result

    def reverse_transform_mcp_server(self, name: str, config: dict) -> McpServer:
        """Transform Gemini config back to unified format."""
        if "httpUrl" in config:
            return McpServer(
                url=config["httpUrl"],
                env=config.get("env"),
            )

        return McpServer(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env"),
        )

    def write_mcp_config(self, servers: dict, path: Path) -> None:
        """Write MCP config to path, merging with existing settings."""
        path.parent.mkdir(parents=True, exist_ok=True)

        existing = {}
        if path.exists():
            existing = json.loads(path.read_text())

        existing[self.mcp_root_key] = servers
        path.write_text(json.dumps(existing, indent=2))

    def generate_root_doc(
        self,
        general_lines: list[str],
        rules_sections: dict[str, list[str]],
        command_sections: dict[str, list[str]],
        output_dir: Path,
    ) -> None:
        """Generate GEMINI.md from rules."""
        content = self.build_root_doc_content(general_lines, rules_sections)
        if content.strip():
            (output_dir / "GEMINI.md").write_text(content)
