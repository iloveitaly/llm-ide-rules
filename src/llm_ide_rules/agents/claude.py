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

    mcp_global_path = ".claude.json"
    mcp_project_path = ".mcp.json"

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Claude Code doesn't support rules, only commands."""
        return False

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
        """Generate CLAUDE.md that references AGENTS.md in all target directories."""
        if not section_globs:
            (output_dir / "CLAUDE.md").write_text("@./AGENTS.md\n")
            return

        # Mirror AgentsAgent directory resolution to write CLAUDE.md alongside each AGENTS.md
        target_dirs = {output_dir}
        from llm_ide_rules.utils import resolve_target_dir

        for section_name in rules_sections:
            glob_pattern = section_globs.get(section_name)
            target_dir = resolve_target_dir(output_dir, glob_pattern)
            target_dirs.add(target_dir)

        for target_dir in target_dirs:
            (target_dir / "CLAUDE.md").write_text("@./AGENTS.md\n")

    def configure_agents_md(self, base_dir: Path) -> bool:
        """Create CLAUDE.md pointing to AGENTS.md wherever AGENTS.md exists and CLAUDE.md doesn't."""
        configured = False
        for agents_md in base_dir.rglob("AGENTS.md"):
            claude_md = agents_md.parent / "CLAUDE.md"
            if not claude_md.exists():
                claude_md.write_text("@./AGENTS.md\n")
                configured = True
        return configured
