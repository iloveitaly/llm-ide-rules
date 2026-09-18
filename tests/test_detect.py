from pathlib import Path

import pytest

from llm_ide_rules.constants import EXPLODE_AGENTS
from llm_ide_rules.detect import (
    describe_resolved_agents,
    detect_active_agents,
    detect_runtime_agent,
    is_antigravity,
    is_claude_code_cloud,
    is_codex,
    is_cursor_cloud,
    is_github_copilot_agent,
    is_opencode,
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


def test_is_claude_code_cloud_from_remote_session_id():
    env = {"CLAUDE_CODE_REMOTE_SESSION_ID": "sess-1"}

    assert is_claude_code_cloud(env) is True
    assert detect_runtime_agent(env) == "claude"


def test_is_claude_code_cloud_from_environment_kind():
    assert is_claude_code_cloud({"CLAUDE_CODE_ENVIRONMENT_KIND": "byoc"}) is True
    assert (
        is_claude_code_cloud({"CLAUDE_CODE_ENVIRONMENT_KIND": "anthropic_cloud"})
        is True
    )


def test_is_claude_code_cloud_from_remote_entrypoint():
    assert is_claude_code_cloud({"CLAUDE_CODE_ENTRYPOINT": "remote"}) is True
    assert is_claude_code_cloud({"CLAUDE_CODE_ENTRYPOINT": "remote_desktop"}) is True


def test_is_claude_code_cloud_rejects_local_cli():
    env = {"CLAUDECODE": "1", "CLAUDE_CODE_ENTRYPOINT": "cli"}

    assert is_claude_code_cloud(env) is False
    assert detect_runtime_agent(env) is None


def test_is_github_copilot_agent_from_session_id():
    env = {"COPILOT_AGENT_SESSION_ID": "sess-1"}

    assert is_github_copilot_agent(env) is True
    assert detect_runtime_agent(env) == "github"


def test_is_github_copilot_agent_from_actions_actor():
    env = {"GITHUB_ACTIONS": "true", "GITHUB_ACTOR": "copilot-swe-agent"}

    assert is_github_copilot_agent(env) is True
    assert detect_runtime_agent(env) == "github"


def test_is_github_copilot_agent_from_workflow_ref():
    env = {
        "GITHUB_ACTIONS": "1",
        "GITHUB_WORKFLOW_REF": "github/copilot-swe-agent/.github/workflows/agent.yml@refs/heads/main",
    }

    assert is_github_copilot_agent(env) is True


def test_is_github_copilot_agent_rejects_plain_actions():
    env = {"GITHUB_ACTIONS": "true", "GITHUB_ACTOR": "octocat"}

    assert is_github_copilot_agent(env) is False
    assert detect_runtime_agent(env) is None


def test_is_opencode_from_env():
    env = {"OPENCODE": "1"}

    assert is_opencode(env) is True
    assert detect_runtime_agent(env) == "opencode"
    assert is_opencode({"OPENCODE_SERVER": "http://127.0.0.1:4096"}) is True


def test_is_antigravity_from_env():
    env = {"ANTIGRAVITY_AGENT": "true"}

    assert is_antigravity(env) is True
    assert detect_runtime_agent(env) == "antigravity"
    assert is_antigravity({"ANTIGRAVITY_PROJECT_ID": "proj-abc"}) is True


def test_is_codex_from_env():
    env = {"CODEX_SANDBOX": "seatbelt"}

    assert is_codex(env) is True
    assert detect_runtime_agent(env) == "codex"
    assert is_codex({"CODEX_CI": "1"}) is True
    assert is_codex({"CODEX_THREAD_ID": "thread-1"}) is True


def test_is_codex_rejects_codex_home():
    assert is_codex({"CODEX_HOME": "/tmp/codex-home"}) is False
    assert detect_runtime_agent({"CODEX_HOME": "/tmp/codex-home"}) is None


def test_detect_runtime_agent_prefers_first_matching_detector():
    env = {
        "CURSOR_CONVERSATION_ID": "bc-test",
        "CLAUDE_CODE_REMOTE_SESSION_ID": "sess-1",
        "OPENCODE": "1",
    }

    assert detect_runtime_agent(env) == "cursor"


@pytest.mark.parametrize(
    ("environ", "agent"),
    [
        ({"CURSOR_CONVERSATION_ID": "bc-test"}, "cursor"),
        ({"CLAUDE_CODE_REMOTE_SESSION_ID": "sess-1"}, "claude"),
        ({"COPILOT_AGENT_SESSION_ID": "sess-1"}, "github"),
        ({"OPENCODE": "1"}, "opencode"),
        ({"ANTIGRAVITY_AGENT": "true"}, "antigravity"),
        ({"CODEX_THREAD_ID": "thread-1"}, "codex"),
    ],
)
def test_resolve_runtime_when_disk_empty(
    tmp_path: Path, environ: dict[str, str], agent: str
):
    agents, source = resolve_target_agents(tmp_path, environ=environ)

    assert source == "runtime"
    assert agents == [agent]


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
