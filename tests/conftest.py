import os

import pytest

# Cursor Cloud injects these into the process; strip them so CLI default-agent
# resolution stays deterministic unless a test opts back in.
CURSOR_CLOUD_ENV_VARS = [
    "CURSOR_AGENT",
    "CURSOR_AGENT_SOCKET",
    "CURSOR_CONVERSATION_ID",
    "CURSOR_AGENT_WORKER_ID",
    "CURSOR_WORKER_POOL_NAME",
    "CURSOR_AGENT_CLI_LOCAL_MODE",
]


@pytest.fixture(autouse=True)
def isolate_runtime_environment(monkeypatch):
    for var in CURSOR_CLOUD_ENV_VARS:
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
