"""Grok CLI agent implementation."""

from llm_ide_rules.agents.dotagents import DotAgentsBaseAgent


class GrokAgent(DotAgentsBaseAgent):
    """Agent for Grok CLI."""

    name = "grok"
