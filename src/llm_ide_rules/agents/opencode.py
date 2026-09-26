"""OpenCode agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    extract_description_and_filter_content,
    extract_frontmatter_description,
    get_ordered_files,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    trim_content,
)


class OpenCodeAgent(BaseAgent):
    """Agent for OpenCode."""

    name = "opencode"
    rules_dir = None
    commands_dir = ".opencode/commands"
    rule_extension = None
    command_extension = ".md"

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        """OpenCode doesn't support rules."""
        return False

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle OpenCode command files (.md) into a single output file."""
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
            file_content = command_file.read_text().strip()
            if not file_content:
                continue

            desc = extract_frontmatter_description(file_content.splitlines())
            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            header = resolve_header_from_stem(
                command_file.stem, section_globs if section_globs else {}
            )
            content_parts.append(f"## {header}\n\n")

            stem_title = resolve_header_from_stem(
                command_file.stem, section_globs if section_globs else {}
            )
            if desc and desc.strip().lower() not in (
                header.strip().lower(),
                stem_title.strip().lower(),
            ):
                content_parts.append(f"Description: {desc}\n\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        self._write_bundled_content(output_file, "".join(content_parts))
        return True

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        """OpenCode doesn't support rules."""

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write an OpenCode command file (.md) with YAML frontmatter."""
        extension = self.command_extension or ".md"
        filepath = commands_dir / f"{filename}{extension}"

        desc, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )

        frontmatter = f"---\ndescription: {desc}\n---\n\n" if desc else ""
        trimmed = trim_content(filtered_content)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(frontmatter + "".join(trimmed))

    def configure_agents_md(self, base_dir: Path) -> bool:
        """OpenCode has native support for AGENTS.md, no configuration changes needed."""
        return True

    def detect(self, base_dir: Path) -> bool:
        "detect if OpenCode is in use in the given directory"
        return (base_dir / ".opencode").exists() or (
            base_dir / "opencode.json"
        ).exists()
