"""Gemini CLI agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_toml_metadata,
    trim_content,
    extract_description_and_filter_content,
)


class GeminiAgent(BaseAgent):
    """Agent for Gemini CLI."""

    name = "gemini"
    rules_dir = None
    commands_dir = ".gemini/commands"
    rule_extension = None
    command_extension = ".toml"

    def bundle_rules(self, output_file: Path, section_globs: dict) -> bool:
        """Gemini CLI doesn't support rules, only commands."""
        return False

    def bundle_commands(self, output_file: Path, section_globs: dict) -> bool:
        """Bundle Gemini CLI command files (.toml) into a single output file."""
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

                content = strip_toml_metadata(content)
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
        filepath = commands_dir / f"{filename}{self.command_extension}"

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

        with open(filepath, "w") as f:
            f.write(f'name = "{filename}"\n')
            if description:
                f.write(f'description = "{description}"\n')
            else:
                f.write(f'description = "{section_name or filename}"\n')
            f.write("\n[command]\n")
            f.write('shell = """\n')
            f.write(content_str)
            f.write('\n"""\n')


