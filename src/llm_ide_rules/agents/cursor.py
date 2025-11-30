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

    def bundle_rules(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """Bundle Cursor rule files (.mdc) into a single output file."""
        rules_path = output_file.parent / self.rules_dir
        rule_files = list(rules_path.glob(f"*{self.rule_extension}"))

        general = [f for f in rule_files if f.stem == "general"]
        others = [f for f in rule_files if f.stem != "general"]

        ordered_others = get_ordered_files(others, list(section_globs.keys()))
        ordered = general + ordered_others

        content_parts: list[str] = []
        for rule_file in ordered:
            content = rule_file.read_text().strip()
            if not content:
                continue

            content = strip_yaml_frontmatter(content)
            content = strip_header(content)
            header = resolve_header_from_stem(rule_file.stem, section_globs)

            if rule_file.stem != "general":
                content_parts.append(f"## {header}\n\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        output_file.write_text("".join(content_parts))
        return True

    def bundle_commands(self, output_file: Path, section_globs: dict[str, str | None]) -> bool:
        """Bundle Cursor command files (.md) into a single output file."""
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
        """Write a Cursor rule file (.mdc) with YAML frontmatter."""
        filepath = rules_dir / f"{filename}{self.rule_extension}"

        if glob_pattern:
            header_yaml = f"""---
description:
globs: {glob_pattern}
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
        filepath = commands_dir / f"{filename}{self.command_extension}"

        trimmed = trim_content(content_lines)

        filtered_content = []
        found_header = False
        for line in trimmed:
            if not found_header and line.startswith("## "):
                found_header = True
                continue
            filtered_content.append(line)

        filtered_content = trim_content(filtered_content)
        filepath.write_text("".join(filtered_content))

    def write_prompt(
        self,
        content_lines: list[str],
        filename: str,
        prompts_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Cursor prompt file (.mdc) with optional frontmatter."""
        filepath = prompts_dir / f"{filename}{self.rule_extension}"

        description, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )

        output_parts: list[str] = []
        if description:
            output_parts.append(f"---\ndescription: {description}\n---\n")

        output_parts.extend(filtered_content)
        filepath.write_text("".join(output_parts))


