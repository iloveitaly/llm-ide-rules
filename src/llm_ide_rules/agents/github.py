"""GitHub/Copilot agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files_github,
    resolve_header_from_stem,
    strip_yaml_frontmatter,
    strip_header,
    write_rule_file,
    extract_description_and_filter_content,
)
from llm_ide_rules.constants import header_to_filename
from llm_ide_rules.mcp import McpServer


class GitHubAgent(BaseAgent):
    """Agent for GitHub Copilot."""

    name = "github"
    rules_dir = ".github/instructions"
    commands_dir = ".github/prompts"
    rule_extension = ".instructions.md"
    command_extension = ".prompt.md"

    mcp_global_path = ".copilot/mcp-config.json"
    mcp_project_path = ".copilot/mcp-config.json"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None]
    ) -> bool:
        """Bundle GitHub instruction files into a single output file."""
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        base_dir = output_file.parent
        instructions_path = base_dir / rules_dir
        copilot_general = base_dir / ".github" / "copilot-instructions.md"

        rule_ext = self.rule_extension
        if not rule_ext:
            return False

        instr_files = list(instructions_path.glob(f"*{rule_ext}"))

        ordered_instructions = get_ordered_files_github(
            instr_files, list(section_globs.keys())
        )

        content_parts: list[str] = []
        if copilot_general.exists():
            content = copilot_general.read_text().strip()
            if content:
                content_parts.append(content)
                content_parts.append("\n\n")

        for instr_file in ordered_instructions:
            content = instr_file.read_text().strip()
            if not content:
                continue

            content = strip_yaml_frontmatter(content)
            content = strip_header(content)
            base_stem = instr_file.stem.replace(".instructions", "")
            header = resolve_header_from_stem(base_stem, section_globs)
            content_parts.append(f"## {header}\n\n")
            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        output_file.write_text("".join(content_parts))
        return True

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None]
    ) -> bool:
        """Bundle GitHub prompt files into a single output file."""
        commands_dir = self.commands_dir
        if not commands_dir:
            return False

        prompts_path = output_file.parent / commands_dir
        if not prompts_path.exists():
            return False

        command_ext = self.command_extension
        if not command_ext:
            return False

        prompt_files = list(prompts_path.glob(f"*{command_ext}"))
        if not prompt_files:
            return False

        prompt_dict = {}
        for f in prompt_files:
            base_stem = f.stem.replace(".prompt", "")
            prompt_dict[base_stem] = f

        ordered_prompts = []
        for section_name in section_globs.keys():
            filename = header_to_filename(section_name)
            if filename in prompt_dict:
                ordered_prompts.append(prompt_dict[filename])
                del prompt_dict[filename]

        remaining_prompts = sorted(prompt_dict.values(), key=lambda p: p.name)
        ordered_prompts.extend(remaining_prompts)

        content_parts: list[str] = []
        for prompt_file in ordered_prompts:
            content = prompt_file.read_text().strip()
            if not content:
                continue

            content = strip_yaml_frontmatter(content)
            content = strip_header(content)
            base_stem = prompt_file.stem.replace(".prompt", "")
            header = resolve_header_from_stem(base_stem, section_globs)
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
        """Write a GitHub instruction file (.instructions.md) with YAML frontmatter."""
        extension = self.rule_extension or ".instructions.md"
        filepath = rules_dir / f"{filename}{extension}"

        if glob_pattern and glob_pattern != "manual":
            header_yaml = f"""---
applyTo: "{glob_pattern}"
---
"""
        else:
            header_yaml = ""

        write_rule_file(filepath, header_yaml, content_lines)

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a GitHub prompt file (.prompt.md) with YAML frontmatter."""
        extension = self.command_extension or ".prompt.md"
        filepath = commands_dir / f"{filename}{extension}"

        description, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )

        frontmatter = f"---\nmode: 'agent'\ndescription: '{description}'\n---\n"
        filepath.write_text(frontmatter + "".join(filtered_content))

    def write_general_instructions(
        self, content_lines: list[str], base_dir: Path
    ) -> None:
        """Write the general copilot-instructions.md file (no frontmatter)."""
        filepath = base_dir / ".github" / "copilot-instructions.md"
        write_rule_file(filepath, "", content_lines)

    def transform_mcp_server(self, server: McpServer) -> dict:
        """Transform unified server to GitHub Copilot format (adds type and tools)."""
        base: dict = {"tools": ["*"]}
        if server.env:
            base["env"] = server.env

        if server.url:
            return {"type": "http", "url": server.url, **base}

        return {
            "type": "local",
            "command": server.command,
            "args": server.args or [],
            **base,
        }

    def reverse_transform_mcp_server(self, name: str, config: dict) -> McpServer:
        """Transform GitHub Copilot config back to unified format."""
        if config.get("type") == "http":
            return McpServer(
                url=config["url"],
                env=config.get("env"),
            )

        return McpServer(
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env"),
        )
