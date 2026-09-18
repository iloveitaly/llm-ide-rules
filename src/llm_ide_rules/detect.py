"""Detect exploded agents on disk and the coding-agent runtime.

Default explode/download target resolution:

1. Explicit CLI selection
2. Agents already exploded on disk
3. Certain runtime environment
4. Fallback (all explode agents, or download DEFAULT_TYPES)

Runtime detectors use vendor-injected env vars, not on-disk rule folders.
They only apply when the target has no exploded agents.
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

# Claude Code maps these kinds/entrypoints to a remote/cloud session
CLAUDE_CLOUD_ENV_KINDS = frozenset({"byoc", "anthropic_cloud"})
CLAUDE_REMOTE_ENTRYPOINTS = frozenset(
    {
        "remote",
        "remote_baku",
        "remote_cowork",
        "remote_desktop",
        "remote_mobile",
        "claude-in-teams",
    }
)

OPENCODE_ENV_VARS = (
    "OPENCODE",
    "OPENCODE_BIN_PATH",
    "OPENCODE_SERVER",
    "OPENCODE_APP_INFO",
    "OPENCODE_MODES",
)

Env = Mapping[str, str]


def _env(environ: Env | None) -> Env:
    return os.environ if environ is None else environ


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _has_value(value: str | None) -> bool:
    return bool(value and value.strip())


def _any_set(env: Env, names: tuple[str, ...]) -> bool:
    return any(_has_value(env.get(name)) for name in names)


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


def is_claude_code_cloud(environ: Env | None = None) -> bool:
    """Return True when this process is a Claude Code remote/cloud session.

    Local CLI/IDE runs use `CLAUDECODE=1` and entrypoints like `cli`. Those are
    not enough on their own.
    """
    env = _env(environ)
    kind = env.get("CLAUDE_CODE_ENVIRONMENT_KIND", "").strip().lower()
    if kind in CLAUDE_CLOUD_ENV_KINDS:
        return True

    entrypoint = env.get("CLAUDE_CODE_ENTRYPOINT", "").strip().lower()
    if entrypoint in CLAUDE_REMOTE_ENTRYPOINTS:
        return True

    return _has_value(env.get("CLAUDE_CODE_REMOTE_SESSION_ID"))


def is_github_copilot_agent(environ: Env | None = None) -> bool:
    """Return True when this process is GitHub Copilot's coding agent.

    Regular GitHub Actions is not enough; the workflow must be the Copilot
    agent, or `COPILOT_AGENT_SESSION_ID` must be set.
    """
    env = _env(environ)
    if _has_value(env.get("COPILOT_AGENT_SESSION_ID")):
        return True

    if not _is_truthy(env.get("GITHUB_ACTIONS")):
        return False

    actor = env.get("GITHUB_ACTOR", "").strip().lower()
    workflow_ref = env.get("GITHUB_WORKFLOW_REF", "").strip().lower()

    return (
        actor == "copilot"
        or "copilot-swe-agent" in actor
        or "copilot-swe-agent" in workflow_ref
    )


def is_opencode(environ: Env | None = None) -> bool:
    "return True when this process was spawned by OpenCode"
    return _any_set(_env(environ), OPENCODE_ENV_VARS)


def is_antigravity(environ: Env | None = None) -> bool:
    "return True when this process was spawned by Antigravity"
    return _any_set(_env(environ), ("ANTIGRAVITY_AGENT", "ANTIGRAVITY_PROJECT_ID"))


def is_codex(environ: Env | None = None) -> bool:
    "return True when this process was spawned by Codex"

    # CODEX_HOME is the user config dir (~/.codex), not a runtime signal
    return _any_set(_env(environ), ("CODEX_SANDBOX", "CODEX_CI", "CODEX_THREAD_ID"))


RUNTIME_DETECTORS: list[tuple[str, Callable[[Env | None], bool]]] = [
    ("cursor", is_cursor_cloud),
    ("claude", is_claude_code_cloud),
    ("github", is_github_copilot_agent),
    ("opencode", is_opencode),
    ("antigravity", is_antigravity),
    ("codex", is_codex),
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
