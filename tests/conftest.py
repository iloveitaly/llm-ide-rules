import os
import pytest

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
