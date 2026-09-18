"""Detect exploded agents on disk and the coding-agent runtime.

Default explode/download target resolution:

1. Explicit CLI selection
2. Agents already exploded on disk
3. Certain runtime environment (Cursor Cloud today)
4. Fallback (all explode agents, or download DEFAULT_TYPES)

Cursor Cloud is identified from vendor-injected env vars, not from `.cursor/`
on disk. Runtime detection only applies when the target has no exploded agents.

Easy follow-ups to wire into `RUNTIME_DETECTORS`:

- Claude Code cloud: `CLAUDE_CODE_REMOTE_SESSION_ID`,
  `CLAUDE_CODE_ENVIRONMENT_KIND` in `{byoc, anthropic_cloud}`, or
  `CLAUDE_CODE_ENTRYPOINT` in `remote_*`
- GitHub Copilot coding agent: `GITHUB_ACTIONS` plus `GITHUB_ACTOR` matching
  `copilot-swe-agent`, or `COPILOT_AGENT_SESSION_ID`
- OpenCode: `OPENCODE`
- Antigravity: `ANTIGRAVITY_AGENT`
"""

import os
from collections.abc import Callable, Mapping
from pathlib import Path

from llm_ide_rules.agents import get_all_agents
from llm_ide_rules.constants import EXPLODE_AGENTS
from llm_ide_rules.log import log

# Documented default metadata socket on Cursor-managed Cloud Agent VMs
CURSOR_CLOUD_SOCKET = "/run/cursor/api.sock"

# Cloud Agent ids (`bcId`) are injected as CURSOR_CONVERSATION_ID
CURSOR_CLOUD_AGENT_ID_PREFIX = "bc-"

Env = Mapping[str, str]


def _env(environ: Env | None) -> Env:
    return os.environ if environ is None else environ


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False

    return value.strip().lower() in {"1", "true", "yes", "on"}


def is_cursor_cloud(environ: Env | None = None) -> bool:
    """Return True when we are certain this process is a Cursor Cloud agent.

    Local Cursor CLI sets `CURSOR_AGENT=1` and `CURSOR_AGENT_CLI_LOCAL_MODE=true`.
    Managed cloud VMs instead inject a `bc-` conversation id, worker-pool vars,
    and/or `CURSOR_AGENT_SOCKET=/run/cursor/api.sock`.
    """
    env = _env(environ)

    # Local CLI marker is a hard veto so we never treat a laptop session as cloud
    if _is_truthy(env.get("CURSOR_AGENT_CLI_LOCAL_MODE")):
        return False

    conversation_id = env.get("CURSOR_CONVERSATION_ID", "")
    if conversation_id.startswith(CURSOR_CLOUD_AGENT_ID_PREFIX):
        return True

    if env.get("CURSOR_AGENT_WORKER_ID") or env.get("CURSOR_WORKER_POOL_NAME"):
        return True

    socket = env.get("CURSOR_AGENT_SOCKET", "")
    return socket == CURSOR_CLOUD_SOCKET or socket.endswith(CURSOR_CLOUD_SOCKET)


RUNTIME_DETECTORS: list[tuple[str, Callable[[Env | None], bool]]] = [
    ("cursor", is_cursor_cloud),
]


def detect_runtime_agent(environ: Env | None = None) -> str | None:
    """Return the agent name if the runtime can be detected with certainty."""
    for agent_name, detector in RUNTIME_DETECTORS:
        if detector(environ):
            return agent_name

    return None


def detect_active_agents(target_dir: Path) -> list[str]:
    "detect agents in use in the target directory"
    detected = []
    explode_agent_names = set(EXPLODE_AGENTS)

    for agent in get_all_agents():
        if agent.name in explode_agent_names and agent.detect(target_dir):
            detected.append(agent.name)

    return detected


def resolve_target_agents(
    working_dir: Path,
    explicit: str | list[str] | None = None,
    fallback: list[str] | None = None,
    environ: Env | None = None,
) -> tuple[list[str], str]:
    """Resolve which agents to explode or download.

    Returns:
        `(agent_names, source)` where source is `explicit`, `runtime`, `disk`,
        or `fallback`.
    """
    if fallback is None:
        fallback = list(EXPLODE_AGENTS)

    if isinstance(explicit, str):
        if explicit == "all":
            return list(fallback), "explicit"

        return [explicit], "explicit"

    if explicit:
        return list(explicit), "explicit"

    detected = detect_active_agents(working_dir)
    if detected:
        log.info("detected active agents in target directory", detected=detected)
        return detected, "disk"

    runtime_agent = detect_runtime_agent(environ)
    if runtime_agent:
        log.info("detected runtime environment", agent=runtime_agent)
        return [runtime_agent], "runtime"

    return list(fallback), "fallback"


def describe_resolved_agents(source: str, agents: list[str]) -> str | None:
    """User-facing reason for a default agent selection, if one should be shown."""
    if source == "runtime":
        return f"Detected runtime environment: {', '.join(agents)}"

    if source == "disk":
        return f"Detected active agents: {', '.join(agents)}"

    return None
