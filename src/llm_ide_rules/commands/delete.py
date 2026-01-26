"""Delete command: Remove downloaded LLM instruction files."""

import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated

from llm_ide_rules.commands.download import INSTRUCTION_TYPES, DEFAULT_TYPES
from llm_ide_rules.log import log


def find_files_to_delete(
    instruction_types: list[str], target_dir: Path
) -> tuple[list[Path], list[Path]]:
    """Find all files and directories that would be deleted.

    Returns:
        Tuple of (directories, files) to delete
    """
    dirs_to_delete = []
    files_to_delete = []

    for inst_type in instruction_types:
        if inst_type not in INSTRUCTION_TYPES:
            log.warning("unknown instruction type", type=inst_type)
            continue

        config = INSTRUCTION_TYPES[inst_type]

        for dir_name in config["directories"]:
            dir_path = target_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                dirs_to_delete.append(dir_path)

        for file_name in config["files"]:
            file_path = target_dir / file_name
            if file_path.exists() and file_path.is_file():
                files_to_delete.append(file_path)

        for file_pattern in config.get("recursive_files", []):
            matching_files = list(target_dir.rglob(file_pattern))
            files_to_delete.extend([f for f in matching_files if f.is_file()])

    return dirs_to_delete, files_to_delete


def delete_main(
    instruction_types: Annotated[
        list[str],
        typer.Argument(
            help="Types of instructions to delete (cursor, github, gemini, claude, agent, agents). Deletes everything by default."
        ),
    ] = None,
    target_dir: Annotated[
        str, typer.Option("--target", "-t", help="Target directory to delete from")
    ] = ".",
    yes: Annotated[
        bool,
        typer.Option(
            "--yes", "-y", help="Skip confirmation prompt and delete immediately"
        ),
    ] = False,
):
    """Remove downloaded LLM instruction files.

    This command removes files and directories that were downloaded by the 'download' command.
    It will show you what will be deleted and ask for confirmation before proceeding.

    Examples:

    \b
    # Delete everything (with confirmation)
    llm_ide_rules delete

    \b
    # Delete only Cursor and Gemini files
    llm_ide_rules delete cursor gemini

    \b
    # Delete without confirmation prompt
    llm_ide_rules delete --yes

    \b
    # Delete from a specific directory
    llm_ide_rules delete --target ./my-project
    """
    if not instruction_types:
        instruction_types = DEFAULT_TYPES

    invalid_types = [t for t in instruction_types if t not in INSTRUCTION_TYPES]
    if invalid_types:
        log.error(
            "invalid instruction types",
            invalid_types=invalid_types,
            valid_types=list(INSTRUCTION_TYPES.keys()),
        )
        raise typer.Exit(1)

    target_path = Path(target_dir).resolve()

    if not target_path.exists():
        log.error("target directory does not exist", target_dir=str(target_path))
        error_msg = f"Target directory does not exist: {target_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    log.info(
        "finding files to delete",
        instruction_types=instruction_types,
        target_dir=str(target_path),
    )

    dirs_to_delete, files_to_delete = find_files_to_delete(
        instruction_types, target_path
    )

    if not dirs_to_delete and not files_to_delete:
        log.info("no files found to delete")
        typer.echo("No matching instruction files found to delete.")
        return

    typer.echo("\nThe following files and directories will be deleted:\n")

    if dirs_to_delete:
        typer.echo("Directories:")
        for dir_path in sorted(dirs_to_delete):
            relative_path = dir_path.relative_to(target_path)
            typer.echo(f"  - {relative_path}/")

    if files_to_delete:
        typer.echo("\nFiles:")
        for file_path in sorted(files_to_delete):
            relative_path = file_path.relative_to(target_path)
            typer.echo(f"  - {relative_path}")

    total_items = len(dirs_to_delete) + len(files_to_delete)
    typer.echo(f"\nTotal: {total_items} items")

    if not yes:
        typer.echo()
        confirm = typer.confirm("Are you sure you want to delete these files?")
        if not confirm:
            log.info("deletion cancelled by user")
            typer.echo("Deletion cancelled.")
            raise typer.Exit(0)

    deleted_count = 0

    for dir_path in dirs_to_delete:
        try:
            log.info("deleting directory", path=str(dir_path))
            shutil.rmtree(dir_path)
            deleted_count += 1
        except Exception as e:
            log.error("failed to delete directory", path=str(dir_path), error=str(e))
            typer.echo(f"Error deleting {dir_path}: {e}", err=True)

    for file_path in files_to_delete:
        try:
            log.info("deleting file", path=str(file_path))
            file_path.unlink()
            deleted_count += 1
        except Exception as e:
            log.error("failed to delete file", path=str(file_path), error=str(e))
            typer.echo(f"Error deleting {file_path}: {e}", err=True)

    success_msg = f"Successfully deleted {deleted_count} of {total_items} items."
    typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
