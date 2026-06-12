"""Agent registry for LLM IDE rules."""

from llm_ide_rules.agents.base import BaseAgent
from llm_ide_rules.agents.cursor import CursorAgent
from llm_ide_rules.agents.github import GitHubAgent
from llm_ide_rules.agents.claude import ClaudeAgent
from llm_ide_rules.agents.gemini import GeminiAgent
from llm_ide_rules.agents.opencode import OpenCodeAgent
from llm_ide_rules.agents.agents import AgentsAgent
from llm_ide_rules.agents.vscode import VSCodeAgent
from llm_ide_rules.agents.antigravity import AntigravityAgent

AGENTS: dict[str, type[BaseAgent]] = {
    "cursor": CursorAgent,
    "github": GitHubAgent,
    "claude": ClaudeAgent,
    "gemini": GeminiAgent,
    "opencode": OpenCodeAgent,
    "agents": AgentsAgent,
    "vscode": VSCodeAgent,
    "antigravity": AntigravityAgent,
    "grok": AntigravityAgent,
}

# Aliases for user-friendly names (e.g. grok for the .agents layout)
AGENT_ALIASES: dict[str, str] = {
    "grok": "antigravity",
}


def get_agent(name: str) -> BaseAgent:
    """Get an agent instance by name. Supports aliases like 'grok'."""
    if name in AGENT_ALIASES:
        name = AGENT_ALIASES[name]
    if name not in AGENTS:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENTS.keys())}")
    return AGENTS[name]()


def get_all_agents() -> list[BaseAgent]:
    """Get instances of all registered agents (deduped by implementation class for aliases like grok)."""
    seen: set[type[BaseAgent]] = set()
    result: list[BaseAgent] = []
    for agent_cls in AGENTS.values():
        if agent_cls not in seen:
            seen.add(agent_cls)
            result.append(agent_cls())
    return result
