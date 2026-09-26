"antigravity CLI agent implementation"

from pathlib import Path

from llm_ide_rules.agents.dotagents import DotAgentsBaseAgent


class AntigravityAgent(DotAgentsBaseAgent):
    """Agent for Antigravity CLI.

    Antigravity reads standing project rules from AGENTS.md and skills from
    `.agents/skills`. It does not load `.agents/rules`.
    """

    name = "antigravity"
    rules_dir = None

    def configure_agents_md(self, base_dir: Path) -> bool:
        "antigravity has native support for AGENTS.md"

        return True

    def detect(self, base_dir: Path) -> bool:
        "detect if Antigravity is in use in the given directory"

        return (
            super().detect(base_dir)
            or (base_dir / ".gemini").exists()
            or (base_dir / ".antigravity").exists()
        )
