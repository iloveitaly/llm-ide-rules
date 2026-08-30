"""Version handling for llm-ide-rules."""

import importlib.metadata
from pathlib import Path


def is_local_source_checkout() -> bool:
    """Check if the code is running from a local source checkout."""
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent.parent

    return (repo_root / ".git").exists() and (repo_root / "pyproject.toml").exists()


def get_version() -> str:
    """Get the version string, appending .dev if running from source."""
    try:
        # Try to get the version of the installed package
        version = importlib.metadata.version("llm-ide-rules")
    except importlib.metadata.PackageNotFoundError:
        # Fallback for local development if not installed
        version = "0.1.0"

    if not is_local_source_checkout():
        return version

    if version.endswith(".dev"):
        return version

    return f"{version}.dev"


get_cli_version = get_version
__version__ = get_version()
