from pathlib import Path

from llm_ide_rules.constants import EXPLODE_AGENTS
from llm_ide_rules.detect import (
    describe_resolved_agents,
    detect_active_agents,
    detect_runtime_agent,
    is_cursor_cloud,
    resolve_target_agents,
)


def test_is_cursor_cloud_from_conversation_id():
    env = {"CURSOR_CONVERSATION_ID": "bc-01a0b438-73f8-7721-983e-5eb5525b63fe"}

    assert is_cursor_cloud(env) is True
    assert detect_runtime_agent(env) == "cursor"


def test_is_cursor_cloud_from_managed_socket():
    env = {"CURSOR_AGENT_SOCKET": "/run/cursor/api.sock"}

    assert is_cursor_cloud(env) is True


def test_is_cursor_cloud_from_worker_id():
    env = {"CURSOR_AGENT_WORKER_ID": "worker-1"}

    assert is_cursor_cloud(env) is True


def test_is_cursor_cloud_rejects_local_cli():
    env = {
        "CURSOR_AGENT": "1",
        "CURSOR_AGENT_CLI_LOCAL_MODE": "true",
        "CURSOR_CONVERSATION_ID": "bc-01a0b438-73f8-7721-983e-5eb5525b63fe",
    }

    assert is_cursor_cloud(env) is False
    assert detect_runtime_agent(env) is None


def test_is_cursor_cloud_rejects_bare_cursor_agent():
    # CURSOR_AGENT is also set in local Cursor terminals
    assert is_cursor_cloud({"CURSOR_AGENT": "1"}) is False
    assert detect_runtime_agent({}) is None


def test_resolve_prefers_disk_over_runtime(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "copilot-instructions.md").touch()

    agents, source = resolve_target_agents(
        tmp_path,
        environ={"CURSOR_CONVERSATION_ID": "bc-test"},
    )

    assert source == "disk"
    assert agents == ["github", "claude"]


def test_resolve_uses_runtime_when_disk_empty(tmp_path: Path):
    agents, source = resolve_target_agents(
        tmp_path,
        environ={"CURSOR_CONVERSATION_ID": "bc-test"},
    )

    assert source == "runtime"
    assert agents == ["cursor"]


def test_resolve_uses_disk_when_no_runtime(tmp_path: Path):
    (tmp_path / ".cursor").mkdir()
    (tmp_path / ".claude").mkdir()

    agents, source = resolve_target_agents(tmp_path, environ={})

    assert source == "disk"
    assert agents == ["cursor", "claude"]


def test_resolve_uses_fallback_when_undetected(tmp_path: Path):
    agents, source = resolve_target_agents(tmp_path, environ={})

    assert source == "fallback"
    assert agents == EXPLODE_AGENTS


def test_resolve_explicit_all_uses_fallback(tmp_path: Path):
    agents, source = resolve_target_agents(
        tmp_path,
        explicit="all",
        fallback=["cursor"],
        environ={"CURSOR_CONVERSATION_ID": "bc-test"},
    )

    assert source == "explicit"
    assert agents == ["cursor"]


def test_resolve_explicit_list(tmp_path: Path):
    agents, source = resolve_target_agents(
        tmp_path,
        explicit=["claude", "github"],
        environ={"CURSOR_CONVERSATION_ID": "bc-test"},
    )

    assert source == "explicit"
    assert agents == ["claude", "github"]


def test_resolve_explicit_agent_wins(tmp_path: Path):
    (tmp_path / ".cursor").mkdir()

    agents, source = resolve_target_agents(
        tmp_path,
        explicit="github",
        environ={"CURSOR_CONVERSATION_ID": "bc-test"},
    )

    assert source == "explicit"
    assert agents == ["github"]


def test_detect_active_agents(tmp_path: Path):
    assert detect_active_agents(tmp_path) == []

    (tmp_path / ".cursor").mkdir()
    assert detect_active_agents(tmp_path) == ["cursor"]

    (tmp_path / ".claude").mkdir()
    assert set(detect_active_agents(tmp_path)) == {"cursor", "claude"}

    (tmp_path / ".github").mkdir()
    assert set(detect_active_agents(tmp_path)) == {"cursor", "claude"}

    (tmp_path / ".github" / "copilot-instructions.md").touch()
    assert set(detect_active_agents(tmp_path)) == {"cursor", "claude", "github"}


def test_describe_resolved_agents():
    assert (
        describe_resolved_agents("runtime", ["cursor"])
        == "Detected runtime environment: cursor"
    )
    assert (
        describe_resolved_agents("disk", ["cursor", "claude"])
        == "Detected active agents: cursor, claude"
    )
    assert describe_resolved_agents("fallback", EXPLODE_AGENTS) is None
    assert describe_resolved_agents("explicit", ["github"]) is None
