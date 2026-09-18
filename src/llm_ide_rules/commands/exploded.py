"""Exploded command: list clients that were exploded/active in the target directory."""

from pathlib import Path
from typing import Annotated

import typer

from llm_ide_rules.environment import detect_active_agents


def exploded_main(
    directory: Annotated[
        str | None,
        typer.Argument(help="Target directory to inspect for exploded clients"),
    ] = None,
    target_dir: Annotated[
        str | None,
        typer.Option(
            "--target",
            "-t",
            help="Target directory to inspect for exploded clients",
        ),
    ] = None,
) -> None:
    "output the list of clients that were exploded"
    target_path = Path(target_dir or directory or ".").resolve()

    if not target_path.exists():
        typer.echo(f"Error: Target directory does not exist: {target_path}", err=True)
        raise typer.Exit(1)

    for client in detect_active_agents(target_path):
        typer.echo(client)
