"""Base agent class and shared utilities for LLM IDE rules."""

import json
from abc import ABC, abstractmethod
from pathlib import Path

from llm_ide_rules.constants import header_to_filename
from llm_ide_rules.mcp import McpServer


class BaseAgent(ABC):
    """Base class for all IDE agents."""

    name: str
    rules_dir: str | None = None
    commands_dir: str | None = None
    rule_extension: str | None = None
    command_extension: str | None = None

    mcp_global_path: str | None = None
    mcp_project_path: str | None = None
    mcp_root_key: str = "mcpServers"

    @abstractmethod
    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None]
    ) -> bool:
        """Bundle rule files into a single output file."""
        ...

    @abstractmethod
    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None]
    ) -> bool:
        """Bundle command files into a single output file."""
        ...

    @abstractmethod
    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
    ) -> None:
        """Write a single rule file."""
        ...

    @abstractmethod
    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a single command file."""
        ...

    def get_rules_path(self, base_dir: Path) -> Path:
        """Get the full path to the rules directory."""
        if not self.rules_dir:
            raise NotImplementedError(f"{self.name} does not support rules")
        return base_dir / self.rules_dir

    def get_commands_path(self, base_dir: Path) -> Path:
        """Get the full path to the commands directory."""
        if not self.commands_dir:
            raise NotImplementedError(f"{self.name} does not support commands")
        return base_dir / self.commands_dir

    def transform_mcp_server(self, server: McpServer) -> dict:
        """Transform unified server to platform-specific format."""
        if server.url:
            result: dict = {"url": server.url}
            if server.env:
                result["env"] = server.env
            return result

        result: dict = {"command": server.command, "args": server.args or []}
        if server.env:
            result["env"] = server.env
        return result

    def reverse_transform_mcp_server(self, name: str, config: dict) -> McpServer:
        """Transform platform config back to unified format."""
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

    def write_mcp_config(self, servers: dict, path: Path) -> None:
        """Write MCP config to path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        config = {self.mcp_root_key: servers}
        path.write_text(json.dumps(config, indent=2))

    def read_mcp_config(self, path: Path) -> dict | None:
        """Read MCP config from path."""
        if not path.exists():
            return None

        config = json.loads(path.read_text())
        return config.get(self.mcp_root_key)


def strip_yaml_frontmatter(text: str) -> str:
    """Strip YAML frontmatter from text."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :]).lstrip("\n")
    return text


def strip_header(text: str) -> str:
    """Remove the first markdown header (## Header) from text if present."""
    lines = text.splitlines()
    if lines and lines[0].startswith("## "):
        remaining_lines = lines[1:]
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines = remaining_lines[1:]
        return "\n".join(remaining_lines)
    return text


def strip_toml_metadata(text: str) -> str:
    """Extract content from TOML prompt block (supports old [command] shell=... and new prompt=...)."""
    import tomllib

    try:
        data = tomllib.loads(text)
        # Check new format
        if "prompt" in data:
            return str(data["prompt"]).strip()
        # Check legacy format
        if (
            "command" in data
            and isinstance(data["command"], dict)
            and "shell" in data["command"]
        ):
            return str(data["command"]["shell"]).strip()
    except Exception:
        pass

    return text.strip()


def get_ordered_files(
    file_list: list[Path], section_globs_keys: list[str]
) -> list[Path]:
    """Order files based on section_globs key order, with unmapped files at the end."""
    file_dict = {f.stem: f for f in file_list}
    ordered_files = []

    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    remaining_files = sorted(file_dict.values(), key=lambda p: p.name)
    ordered_files.extend(remaining_files)

    return ordered_files


def get_ordered_files_github(
    file_list: list[Path], section_globs_keys: list[str]
) -> list[Path]:
    """Order GitHub instruction files, handling .instructions suffix."""
    file_dict = {}
    for f in file_list:
        base_stem = f.stem.replace(".instructions", "")
        file_dict[base_stem] = f

    ordered_files = []

    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    remaining_files = sorted(file_dict.values(), key=lambda p: p.name)
    ordered_files.extend(remaining_files)

    return ordered_files


def resolve_header_from_stem(stem: str, section_globs: dict[str, str | None]) -> str:
    """Return the canonical header for a given filename stem.

    Prefer exact header names from section_globs (preserves acronyms like FastAPI, TypeScript).
    Fallback to title-casing the filename when not found in section_globs.
    """
    for section_name in section_globs.keys():
        if header_to_filename(section_name) == stem:
            return section_name

    return stem.replace("-", " ").title()


def trim_content(content_lines: list[str]) -> list[str]:
    """Remove leading and trailing empty lines from content."""
    start = 0
    for i, line in enumerate(content_lines):
        if line.strip():
            start = i
            break
    else:
        return []

    end = len(content_lines)
    for i in range(len(content_lines) - 1, -1, -1):
        if content_lines[i].strip():
            end = i + 1
            break

    return content_lines[start:end]


def write_rule_file(path: Path, header_yaml: str, content_lines: list[str]) -> None:
    """Write a rule file with front matter and content."""
    trimmed_content = trim_content(content_lines)
    output = header_yaml.strip() + "\n" + "".join(trimmed_content)
    path.write_text(output)


def replace_header_with_proper_casing(
    content_lines: list[str], proper_header: str
) -> list[str]:
    """Replace the first header in content with the properly cased version."""
    if not content_lines:
        return content_lines

    for i, line in enumerate(content_lines):
        if line.startswith("## "):
            content_lines[i] = f"## {proper_header}\n"
            break

    return content_lines


def extract_description_and_filter_content(
    content_lines: list[str], default_description: str
) -> tuple[str, list[str]]:
    """Extract description from first non-empty line that starts with 'Description:' and return filtered content."""
    trimmed_content = trim_content(content_lines)
    description = ""
    description_line = None

    for i, line in enumerate(trimmed_content):
        stripped_line = line.strip()
        if (
            stripped_line
            and not stripped_line.startswith("#")
            and not stripped_line.startswith("##")
        ):
            if stripped_line.startswith("Description:"):
                description = stripped_line[len("Description:") :].strip()
                description_line = i
                break
            else:
                break

    if description and description_line is not None:
        filtered_content = (
            trimmed_content[:description_line] + trimmed_content[description_line + 1 :]
        )
        filtered_content = trim_content(filtered_content)
    else:
        filtered_content = trimmed_content

    return description, filtered_content
