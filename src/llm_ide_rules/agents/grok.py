"grok CLI agent implementation"

from pathlib import Path

from llm_ide_rules.agents.dotagents import DotAgentsBaseAgent


class GrokAgent(DotAgentsBaseAgent):
    "agent for Grok CLI"

    name = "grok"

    def detect(self, base_dir: Path) -> bool:
        "detect if Grok CLI is in use in the given directory"

        return (base_dir / ".grok").exists()
