"""Agent registry for LLM IDE rules."""

from llm_ide_rules.agents.base import BaseAgent
from llm_ide_rules.agents.cursor import CursorAgent
from llm_ide_rules.agents.github import GitHubAgent
from llm_ide_rules.agents.claude import ClaudeAgent
from llm_ide_rules.agents.gemini import GeminiAgent
from llm_ide_rules.agents.opencode import OpenCodeAgent

AGENTS: dict[str, type[BaseAgent]] = {
    "cursor": CursorAgent,
    "github": GitHubAgent,
    "claude": ClaudeAgent,
    "gemini": GeminiAgent,
    "opencode": OpenCodeAgent,
}


def get_agent(name: str) -> BaseAgent:
    """Get an agent instance by name."""
    if name not in AGENTS:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENTS.keys())}")
    return AGENTS[name]()


def get_all_agents() -> list[BaseAgent]:
    """Get instances of all registered agents."""
    return [agent_cls() for agent_cls in AGENTS.values()]
