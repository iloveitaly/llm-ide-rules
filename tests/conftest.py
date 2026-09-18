import os

import pytest

# Vendor agent runtimes inject these; strip them so CLI default-agent
# resolution stays deterministic unless a test opts back in.
RUNTIME_ENV_VARS = [
    "CURSOR_AGENT",
    "CURSOR_AGENT_SOCKET",
    "CURSOR_CONVERSATION_ID",
    "CURSOR_AGENT_WORKER_ID",
    "CURSOR_WORKER_POOL_NAME",
    "CURSOR_AGENT_CLI_LOCAL_MODE",
    "CLAUDECODE",
    "CLAUDE_CODE_REMOTE_SESSION_ID",
    "CLAUDE_CODE_ENVIRONMENT_KIND",
    "CLAUDE_CODE_ENTRYPOINT",
    "GITHUB_ACTIONS",
    "GITHUB_ACTOR",
    "GITHUB_WORKFLOW_REF",
    "COPILOT_AGENT_SESSION_ID",
    "OPENCODE",
    "OPENCODE_BIN_PATH",
    "OPENCODE_SERVER",
    "OPENCODE_APP_INFO",
    "OPENCODE_MODES",
    "ANTIGRAVITY_AGENT",
    "ANTIGRAVITY_PROJECT_ID",
]


@pytest.fixture(autouse=True)
def isolate_runtime_environment(monkeypatch):
    for var in RUNTIME_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(autouse=True)
def ensure_cwd_is_restored():
    """
    Ensure the current working directory is restored after every test.
    This prevents tests that use os.chdir(temp_dir) from breaking subsequent tests
    when the temp_dir is deleted.
    """
    original_cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(original_cwd)
