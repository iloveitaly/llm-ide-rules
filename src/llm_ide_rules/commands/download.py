"""Download command: Download LLM instruction files from GitHub repositories."""

import re
import tempfile
import zipfile
from pathlib import Path

import requests
import typer
from typing_extensions import Annotated

from llm_ide_rules.commands.explode import explode_implementation
from llm_ide_rules.constants import VALID_AGENTS
from llm_ide_rules.log import log

DEFAULT_REPO = "iloveitaly/llm-ide-rules"
DEFAULT_BRANCH = "master"


def normalize_repo(repo: str) -> str:
    """Normalize repository input to user/repo format.

    Handles both formats:
    - user/repo (unchanged)
    - https://github.com/user/repo/ (extracts user/repo)
    """
    # If it's already in user/repo format, return as-is
    if "/" in repo and not repo.startswith("http"):
        return repo

    # Extract user/repo from GitHub URL
    github_pattern = r"https?://github\.com/([^/]+/[^/]+)/?.*"
    match = re.match(github_pattern, repo)

    if match:
        return match.group(1)

    # If no pattern matches, assume it's already in the correct format
    return repo


# Define what files/directories each instruction type includes
# For agents supported by 'explode' (cursor, github, gemini, claude, opencode),
# we don't download specific directories anymore. Instead, we download the source
# files (instructions.md, commands.md) and generate them locally using explode.
# The directories listed here are what gets created by explode and what delete removes.
INSTRUCTION_TYPES = {
    "cursor": {
        "directories": [".cursor/rules", ".cursor/commands"],
        "files": [],
        "include_patterns": [],
    },
    "github": {
        "directories": [".github/instructions", ".github/prompts"],
        "files": [".github/copilot-instructions.md"],
        "include_patterns": [],
    },
    "gemini": {
        "directories": [".gemini/commands"],
        "files": [],
        "generated_files": ["GEMINI.md"],
        "include_patterns": [],
    },
    "claude": {
        "directories": [".claude/commands"],
        "files": [],
        "generated_files": ["CLAUDE.md"],
        "include_patterns": [],
    },
    "opencode": {
        "directories": [".opencode/commands"],
        "files": [],
        "include_patterns": [],
    },
    "agents": {"directories": [], "files": [], "generated_files": ["AGENTS.md"]},
}

# Default types to download when no specific types are specified
DEFAULT_TYPES = list(INSTRUCTION_TYPES.keys())


def download_and_extract_repo(repo: str, branch: str = DEFAULT_BRANCH) -> Path:
    """Download a GitHub repository as a ZIP and extract it to a temporary directory."""
    normalized_repo = normalize_repo(repo)
    zip_url = f"https://github.com/{normalized_repo}/archive/{branch}.zip"

    log.info(
        "downloading repository",
        repo=repo,
        normalized_repo=normalized_repo,
        branch=branch,
        url=zip_url,
    )

    try:
        response = requests.get(zip_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        log.error("failed to download repository", error=str(e), url=zip_url)
        raise typer.Exit(1)

    # Create temporary directory and file
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / "repo.zip"

    # Write ZIP content
    zip_path.write_bytes(response.content)

    # Extract ZIP
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find the extracted repository directory (should be the only directory)
    repo_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if not repo_dirs:
        log.error("no directories found in extracted zip")
        raise typer.Exit(1)

    repo_dir = repo_dirs[0]
    log.info("repository extracted", path=str(repo_dir))

    return repo_dir


def copy_instruction_files(
    repo_dir: Path, instruction_types: list[str], target_dir: Path
):
    """Copy instruction files from the repository to the target directory."""
    copied_items = []

    for inst_type in instruction_types:
        if inst_type not in INSTRUCTION_TYPES:
            log.warning("unknown instruction type", type=inst_type)
            continue

        config = INSTRUCTION_TYPES[inst_type]

        # Copy directories
        for dir_name in config["directories"]:
            source_dir = repo_dir / dir_name
            target_subdir = target_dir / dir_name

            if source_dir.exists():
                log.info(
                    "copying directory",
                    source=str(source_dir),
                    target=str(target_subdir),
                )

                # Create target directory
                target_subdir.mkdir(parents=True, exist_ok=True)

                # Copy all files from source to target
                copy_directory_contents(
                    source_dir,
                    target_subdir,
                    config.get("exclude_patterns", []),
                    config.get("include_patterns", []),
                )
                copied_items.append(f"{dir_name}/")

        # Copy individual files
        for file_name in config["files"]:
            source_file = repo_dir / file_name
            target_file = target_dir / file_name

            if source_file.exists():
                log.info(
                    "copying file", source=str(source_file), target=str(target_file)
                )

                # Create parent directories if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                target_file.write_bytes(source_file.read_bytes())
                copied_items.append(file_name)

        # Copy recursive files (search throughout repository)
        for file_pattern in config.get("recursive_files", []):
            copied_recursive = copy_recursive_files(repo_dir, target_dir, file_pattern)
            copied_items.extend(copied_recursive)

    return copied_items


def copy_recursive_files(
    repo_dir: Path, target_dir: Path, file_pattern: str
) -> list[str]:
    """Recursively copy files matching pattern, preserving directory structure.

    Only copies files to locations where the target directory already exists.
    Warns and skips files where target directories don't exist.

    Args:
        repo_dir: Source repository directory
        target_dir: Target directory to copy to
        file_pattern: File pattern to search for (e.g., "AGENTS.md")

    Returns:
        List of copied file paths relative to target_dir
    """
    copied_items = []

    # Find all matching files recursively
    matching_files = list(repo_dir.rglob(file_pattern))

    for source_file in matching_files:
        # Calculate relative path from repo root
        relative_path = source_file.relative_to(repo_dir)
        target_file = target_dir / relative_path

        # Check if target directory already exists
        target_parent = target_file.parent
        if not target_parent.exists():
            log.warning(
                "target directory does not exist, skipping file copy",
                target_directory=str(target_parent),
                file=str(relative_path),
            )
            continue

        log.info(
            "copying recursive file", source=str(source_file), target=str(target_file)
        )

        # Copy file (parent directory already exists)
        target_file.write_bytes(source_file.read_bytes())
        copied_items.append(str(relative_path))

    return copied_items


def copy_directory_contents(
    source_dir: Path,
    target_dir: Path,
    exclude_patterns: list[str],
    include_patterns: list[str] = [],
):
    """Recursively copy directory contents, excluding specified patterns."""
    for item in source_dir.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(source_dir)
            relative_str = str(relative_path)

            # Check if file matches any exclude pattern
            should_exclude = False
            pattern = ""
            for pattern in exclude_patterns:
                if pattern.endswith("/*"):
                    # Pattern like "workflows/*" - exclude if path starts with "workflows/"
                    pattern_prefix = pattern[:-1]  # Remove the "*"
                    if relative_str.startswith(pattern_prefix):
                        should_exclude = True
                        break
                elif relative_str == pattern:
                    should_exclude = True
                    break

            if should_exclude:
                log.debug("excluding file", file=relative_str, pattern=pattern)
                continue

            # Check if file matches any include pattern (if any provided)
            if include_patterns:
                matched_include = False
                for include_pattern in include_patterns:
                    # Match against filename only, or full relative path
                    if item.match(include_pattern):
                        matched_include = True
                        break

                if not matched_include:
                    log.debug(
                        "skipping file (not matched in include_patterns)",
                        file=relative_str,
                    )
                    continue

            target_file = target_dir / relative_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_bytes(item.read_bytes())


def download_main(
    instruction_types: Annotated[
        list[str] | None,
        typer.Argument(
            help="Types of instructions to download (cursor, github, gemini, claude, opencode, agents). Downloads everything by default."
        ),
    ] = None,
    repo: Annotated[
        str, typer.Option("--repo", "-r", help="GitHub repository to download from")
    ] = DEFAULT_REPO,
    branch: Annotated[
        str, typer.Option("--branch", "-b", help="Branch to download from")
    ] = DEFAULT_BRANCH,
    target_dir: Annotated[
        str, typer.Option("--target", "-t", help="Target directory to download to")
    ] = ".",
):
    """Download LLM instruction files from GitHub repositories.

    This command replaces the legacy download.sh script and provides more flexibility
    in selecting what to download and from which repository.

    Examples:

    \b
    # Download everything from the default repository
    llm_ide_rules download

    \b
    # Download only Cursor and GitHub instructions
    llm_ide_rules download cursor github

    \b
    # Download from a different repository
    llm_ide_rules download --repo other-user/other-repo

    \b
    # Download to a specific directory
    llm_ide_rules download --target ./my-project
    """
    # Use default types if none specified
    if not instruction_types:
        instruction_types = DEFAULT_TYPES

    # Validate instruction types
    invalid_types = [t for t in instruction_types if t not in INSTRUCTION_TYPES]
    if invalid_types:
        log.error(
            "invalid instruction types",
            invalid_types=invalid_types,
            valid_types=list(INSTRUCTION_TYPES.keys()),
        )
        error_msg = f"Invalid instruction types: {', '.join(invalid_types)}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    target_path = Path(target_dir).resolve()

    log.info(
        "starting download",
        repo=repo,
        branch=branch,
        instruction_types=instruction_types,
        target_dir=str(target_path),
    )

    # Download and extract repository
    repo_dir = download_and_extract_repo(repo, branch)

    try:
        # Copy instruction files
        copied_items = [
            f"Downloaded: {item}"
            for item in copy_instruction_files(repo_dir, instruction_types, target_path)
        ]

        # Check for source files (instructions.md, commands.md) and copy them if available
        # These are needed for 'explode' logic
        source_files = ["instructions.md", "commands.md"]
        sources_copied = False

        # Only copy source files if we have at least one agent that uses explode
        has_explode_agent = any(t in VALID_AGENTS for t in instruction_types)

        if has_explode_agent:
            for source_file in source_files:
                src = repo_dir / source_file
                dst = target_path / source_file
                if src.exists():
                    log.info("copying source file", source=str(src), target=str(dst))
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
                    copied_items.append(f"Downloaded: {source_file}")
                    sources_copied = True

        # Generate rule files locally for supported agents
        explodable_agents = [t for t in instruction_types if t in VALID_AGENTS]

        if explodable_agents:
            if not sources_copied:
                # Check if they existed in target already?
                if not (target_path / "instructions.md").exists():
                    log.warning(
                        "source file instructions.md missing, generation might fail"
                    )

            for agent in explodable_agents:
                log.info("generating rules locally", agent=agent)
                try:
                    explode_implementation(
                        input_file="instructions.md",
                        agent=agent,
                        working_dir=target_path,
                    )
                    copied_items.append(f"Generated: {agent} rules")
                except Exception as e:
                    log.error("failed to generate rules", agent=agent, error=str(e))
                    typer.echo(
                        f"Warning: Failed to generate rules for {agent}: {e}", err=True
                    )

        if copied_items:
            success_msg = f"Downloaded/Generated items in {target_path}:"
            typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
            for item in copied_items:
                typer.echo(f"  - {item}")
        else:
            log.info("no files were copied or generated")

            # Build list of expected files
            expected_files = []
            for inst_type in instruction_types:
                config = INSTRUCTION_TYPES[inst_type]
                expected_files.extend(config.get("directories", []))
                expected_files.extend(config.get("files", []))
                expected_files.extend(config.get("recursive_files", []))

            error_msg = "No matching instruction files found in the repository."
            typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)

            if expected_files:
                typer.echo("\nExpected files/directories:", err=True)
                for expected in expected_files:
                    typer.echo(f"  - {expected}", err=True)

    finally:
        # Clean up temporary directory
        import shutil

        shutil.rmtree(repo_dir.parent.parent, ignore_errors=True)
