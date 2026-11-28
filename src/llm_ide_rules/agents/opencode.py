"openCode agent implementation"

from pathlib import Path

from llm_ide_rules.agents.base import BaseAgent


class OpenCodeAgent(BaseAgent):
    """Agent for OpenCode.

    Standing project rules live in AGENTS.md. OpenCode has no vendor-specific
    rules directory.
    """

    name = "opencode"
    rules_dir = None
    rule_extension = None

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        "openCode doesn't support a vendor rules directory"

        return False

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        "openCode doesn't support a vendor rules directory"

    def configure_agents_md(self, base_dir: Path) -> bool:
        "openCode has native support for AGENTS.md, no configuration changes needed"

        return True

    def detect(self, base_dir: Path) -> bool:
        "detect if OpenCode is in use in the given directory"

        return (base_dir / ".opencode").exists() or (
            base_dir / "opencode.json"
        ).exists()
