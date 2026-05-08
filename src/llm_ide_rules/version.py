"""Version handling for llm-ide-rules."""

from pathlib import Path

__version__ = "0.13.0"


def is_local_source_checkout() -> bool:
    """Check if the code is running from a local source checkout."""
    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent.parent

    return (repo_root / ".git").exists() and (repo_root / "pyproject.toml").exists()


def get_cli_version() -> str:
    """Get the version string, appending .dev if running from source."""
    if not is_local_source_checkout():
        return __version__

    if __version__.endswith(".dev"):
        return __version__

    return f"{__version__}.dev"
