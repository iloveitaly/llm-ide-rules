"codex CLI agent implementation"

from pathlib import Path

from llm_ide_rules.agents.dotagents import DotAgentsBaseAgent


class CodexAgent(DotAgentsBaseAgent):
    """Agent for OpenAI Codex.

    Codex reads standing project rules from AGENTS.md and skills from
    `.agents/skills`. It does not load `.agents/rules`.
    """

    name = "codex"
    rules_dir = None

    def configure_agents_md(self, base_dir: Path) -> bool:
        "codex has native support for AGENTS.md"

        return True

    def detect(self, base_dir: Path) -> bool:
        "detect if Codex is in use in the given directory"

        return (base_dir / ".codex").exists()
