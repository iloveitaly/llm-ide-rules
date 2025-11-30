"""Claude Code agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    trim_content,
)


class ClaudeAgent(BaseAgent):
    """Agent for Claude Code."""

    name = "claude"
    rules_dir = None
    commands_dir = ".claude/commands"
    rule_extension = None
    command_extension = ".md"

    def bundle_rules(self, output_file: Path, section_globs: dict) -> bool:
        """Claude Code doesn't support rules, only commands."""
        return False

    def bundle_commands(self, output_file: Path, section_globs: dict) -> bool:
        """Bundle Claude Code command files (.md) into a single output file."""
        commands_path = output_file.parent / self.commands_dir
        if not commands_path.exists():
            return False

        command_files = list(commands_path.glob(f"*{self.command_extension}"))
        if not command_files:
            return False

        ordered_commands = get_ordered_files(command_files, list(section_globs.keys()))

        content_written = False
        with open(output_file, "w") as out:
            for command_file in ordered_commands:
                content = command_file.read_text().strip()
                if not content:
                    continue

                header = resolve_header_from_stem(command_file.stem, section_globs)
                out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")
                content_written = True

        return content_written

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
    ) -> None:
        """Claude Code doesn't support rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a Claude Code command file (.md) - plain markdown, no frontmatter."""
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

        with open(filepath, "w") as f:
            for line in filtered_content:
                f.write(line)

