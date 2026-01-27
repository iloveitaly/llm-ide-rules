"""Cursor IDE agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_yaml_frontmatter,
    strip_header,
    trim_content,
    write_rule_file,
    extract_description_and_filter_content,
)


class CursorAgent(BaseAgent):
    """Agent for Cursor IDE."""

    name = "cursor"
    rules_dir = ".cursor/rules"
    commands_dir = ".cursor/commands"
    rule_extension = ".mdc"
    command_extension = ".md"

    mcp_global_path = ".cursor/mcp.json"
    mcp_project_path = ".cursor/mcp.json"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Cursor rule files (.mdc) into a single output file."""
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        rules_path = output_file.parent / rules_dir

        rule_ext = self.rule_extension
        if not rule_ext:
            return False

        rule_files = list(rules_path.glob(f"*{rule_ext}"))

        general = [f for f in rule_files if f.stem == "general"]
        others = [f for f in rule_files if f.stem != "general"]

        ordered_others = get_ordered_files(
            others, list(section_globs.keys()) if section_globs else None
        )
        ordered = general + ordered_others

        content_parts: list[str] = []
        for rule_file in ordered:
            file_content = rule_file.read_text().strip()
            if not file_content:
                continue

            lines = file_content.splitlines()
            extracted_header = None
            glob_pattern = None

            for line in lines:
                if line.startswith("## "):
                    extracted_header = line[3:].strip()
                    break

            glob_pattern = self._extract_glob_from_frontmatter(file_content)

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            if extracted_header:
                header = extracted_header
            else:
                header = resolve_header_from_stem(
                    rule_file.stem, section_globs if section_globs else {}
                )

            if rule_file.stem != "general":
                content_parts.append(f"## {header}\n\n")
                if glob_pattern:
                    content_parts.append(f"globs: {glob_pattern}\n\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        output_file.write_text("".join(content_parts))
        return True

    def _extract_glob_from_frontmatter(self, content: str) -> str | None:
        """Extract glob pattern from YAML frontmatter."""
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                break
            if lines[i].startswith("globs:"):
                glob_value = lines[i][6:].strip()
                return glob_value if glob_value else None

        return None

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Cursor command files (.md) into a single output file."""
        commands_dir = self.commands_dir
        if not commands_dir:
            return False

        commands_path = output_file.parent / commands_dir
        if not commands_path.exists():
            return False

        command_ext = self.command_extension
        if not command_ext:
            return False

        command_files = list(commands_path.glob(f"*{command_ext}"))
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
        """Write a Cursor rule file (.mdc) with YAML frontmatter."""
        extension = self.rule_extension or ".mdc"
        filepath = rules_dir / f"{filename}{extension}"

        if glob_pattern and glob_pattern != "manual":
            header_yaml = f"""---
description:
globs: {glob_pattern}
alwaysApply: false
---
"""
        elif glob_pattern == "manual":
            header_yaml = """---
description:
alwaysApply: false
---
"""
        else:
            header_yaml = """---
description:
alwaysApply: true
---
"""
        write_rule_file(filepath, header_yaml, content_lines)

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Cursor command file (.md) - plain markdown, no frontmatter."""
        extension = self.command_extension or ".md"
        filepath = commands_dir / f"{filename}{extension}"

        trimmed = trim_content(content_lines)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("".join(trimmed))

    def write_prompt(
        self,
        content_lines: list[str],
        filename: str,
        prompts_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Cursor prompt file (.mdc) with optional frontmatter."""
        extension = self.rule_extension or ".mdc"
        filepath = prompts_dir / f"{filename}{extension}"

        description, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )

        output_parts: list[str] = []
        if description:
            output_parts.append(f"---\ndescription: {description}\n---\n")

        output_parts.extend(filtered_content)
        filepath.write_text("".join(output_parts))
