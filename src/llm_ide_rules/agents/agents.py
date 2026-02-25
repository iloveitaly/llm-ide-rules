"""Agents documentation agent implementation."""

from pathlib import Path
import typer

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
        description: str | None = None,
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
        section_globs: dict[str, str | None] | None = None,
    ) -> None:
        """Generate AGENTS.md files, potentially distributed based on globs."""
        if not section_globs:
            # Fallback to single root AGENTS.md
            content = self.build_root_doc_content(general_lines, rules_sections)
            if content.strip():
                (output_dir / "AGENTS.md").write_text(content)
            return

        # Group rules by target directory
        rules_by_dir: dict[Path, dict[str, list[str]]] = {}

        # Always include root directory for rules without specific directory targets
        rules_by_dir[output_dir] = {}

        from llm_ide_rules.utils import resolve_target_dir

        for section_name, lines in rules_sections.items():
            glob_pattern = section_globs.get(section_name)
            target_dir = resolve_target_dir(output_dir, glob_pattern)

            if target_dir != output_dir and glob_pattern and "**" in glob_pattern:
                prefix = glob_pattern.split("**")[0].strip("/")
                potential_dir = output_dir / prefix
                if target_dir != potential_dir:
                    rel_potential = potential_dir.relative_to(output_dir)
                    rel_actual = target_dir.relative_to(output_dir)
                    typer.secho(
                        f"Warning: Directory '{rel_potential}' for section '{section_name}' does not exist. "
                        f"Placing in '{rel_actual}' instead.",
                        fg=typer.colors.YELLOW,
                        err=True,
                    )

            if target_dir not in rules_by_dir:
                rules_by_dir[target_dir] = {}

            rules_by_dir[target_dir][section_name] = lines

        # Generate AGENTS.md for each directory
        for target_dir, sections in rules_by_dir.items():
            if not sections:
                continue

            # Only include general instructions in the root AGENTS.md
            current_general_lines = general_lines if target_dir == output_dir else []

            content = self.build_root_doc_content(current_general_lines, sections)
            if content.strip():
                (target_dir / "AGENTS.md").write_text(content)
