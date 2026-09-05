"""Antigravity CLI agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.dotagents import DotAgentsBaseAgent


class AntigravityAgent(DotAgentsBaseAgent):
    """Agent for Antigravity CLI."""

    name = "antigravity"

    def detect(self, base_dir: Path) -> bool:
        "detect if Antigravity is in use in the given directory"
        return (
            super().detect(base_dir)
            or (base_dir / ".gemini").exists()
            or (base_dir / ".antigravity").exists()
        )

