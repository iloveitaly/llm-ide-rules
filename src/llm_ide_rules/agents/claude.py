"""Claude Code agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    trim_content,
)


class ClaudeAgent(BaseAgent):
    """Agent for Claude Code."""

    name = "claude"
    rules_dir = ".claude/rules"
    commands_dir = ".claude/commands"
    rule_extension = ".md"
    command_extension = ".md"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Claude Code rule files (.md) into a single output file."""
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        rules_path = output_file.parent / rules_dir
        if not rules_path.exists():
            return False

        extension = self.rule_extension
        if not extension:
            return False

        rule_files = list(rules_path.rglob(f"*{extension}"))
        if not rule_files:
            return False

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

            paths = self._extract_paths_from_frontmatter(file_content)
            extracted_header = None
            for line in file_content.splitlines():
                if line.startswith("## "):
                    extracted_header = line[3:].strip()
                    break

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            if rule_file.stem != "general":
                header = extracted_header or resolve_header_from_stem(
                    rule_file.stem, section_globs if section_globs else {}
                )
                content_parts.append(f"## {header}\n\n")

                if paths:
                    content_parts.append(f"globs: {paths[0]}\n\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        output_file.write_text("".join(content_parts))
        return True

    def _extract_paths_from_frontmatter(self, content: str) -> list[str]:
        """Extract paths entries from YAML frontmatter."""
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return []

        paths: list[str] = []
        in_paths = False

        for i in range(1, len(lines)):
            line = lines[i]
            stripped = line.strip()

            if stripped == "---":
                break

            if stripped == "paths:":
                in_paths = True
                continue

            if not in_paths:
                continue

            if line.startswith("  - "):
                path = stripped[2:].strip().strip('"').strip("'")
                if path:
                    paths.append(path)
                continue

            if stripped:
                in_paths = False

        return paths

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Claude Code command files (.md) into a single output file."""
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
        description: str | None = None,
    ) -> None:
        """Write a Claude Code rule file (.md)."""
        extension = self.rule_extension or ".md"
        filepath = rules_dir / f"{filename}{extension}"

        trimmed = trim_content(content_lines)

        output_parts: list[str] = []
        if glob_pattern and glob_pattern != "manual":
            output_parts.append("---\npaths:\n")
            output_parts.append(f'  - "{glob_pattern}"\n')
            output_parts.append("---\n\n")

        output_parts.extend(trimmed)

        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("".join(output_parts))

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Claude Code command file (.md) - plain markdown, no frontmatter."""
        extension = self.command_extension or ".md"
        filepath = commands_dir / f"{filename}{extension}"

        trimmed = trim_content(content_lines)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text("".join(trimmed))

    def generate_root_doc(
        self,
        general_lines: list[str],
        rules_sections: dict[str, list[str]],
        command_sections: dict[str, list[str]],
        output_dir: Path,
        section_globs: dict[str, str | None] | None = None,
    ) -> None:
        """Claude rules replace CLAUDE.md generation."""
        return

    def configure_agents_md(self, base_dir: Path) -> bool:
        """Claude no longer needs AGENTS.md mirroring files."""
        return False
