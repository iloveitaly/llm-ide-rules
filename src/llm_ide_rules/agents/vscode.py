"""VS Code agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import BaseAgent
class VSCodeAgent(BaseAgent):
    """Agent for VS Code."""

    name = "vscode"
    rules_dir = None  # VS Code typically uses .github (handled by GitHubAgent)
    commands_dir = None
    rule_extension = None
    command_extension = None

    def bundle_rules(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """VS Code doesn't support rules directly (uses GitHub Copilot)."""
        return False

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """VS Code doesn't support commands directly."""
        return False

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        """VS Code doesn't support rules."""
        pass

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """VS Code doesn't support commands."""
        pass
