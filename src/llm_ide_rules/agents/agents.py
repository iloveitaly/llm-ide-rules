"""Agents documentation agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import BaseAgent


class AgentsAgent(BaseAgent):
    """Agent for generating AGENTS.md documentation."""

    name = "agents"
    rules_dir = None
    commands_dir = None
    rule_extension = None
    command_extension = None

    mcp_global_path = None
    mcp_project_path = None

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Agents doesn't support bundling rules."""
        return False

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Agents doesn't support bundling commands."""
        return False

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
    ) -> None:
        """Agents doesn't support writing rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Agents doesn't support writing commands."""
        pass

    def generate_root_doc(
        self,
        general_lines: list[str],
        rules_sections: dict[str, list[str]],
        command_sections: dict[str, list[str]],
        output_dir: Path,
    ) -> None:
        """Generate AGENTS.md from rules."""
        content = self.build_root_doc_content(general_lines, rules_sections)
        if content.strip():
            (output_dir / "AGENTS.md").write_text(content)
