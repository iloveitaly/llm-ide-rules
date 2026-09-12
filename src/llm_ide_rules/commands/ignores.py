import io
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Annotated
from unittest.mock import patch

import typer

from llm_ide_rules.commands.download import detect_active_agents
from llm_ide_rules.commands.explode import explode_implementation
from llm_ide_rules.log import log


def ignores_main(
    input_file: Annotated[
        str, typer.Argument(help="Input markdown file")
    ] = "instructions.md",
    agent: Annotated[
        str | None,
        typer.Option(
            "--agent",
            "-a",
            help="Agent to list ignores for (cursor, github, claude, opencode, or all). Defaults to detecting active agents.",
        ),
    ] = None,
    print_output: Annotated[
        bool,
        typer.Option(
            "--print",
            help="Print the list of files to stdout instead of updating .gitignore",
        ),
    ] = False,
) -> None:
    """Generate a list of files that should be ignored by dry-running the explode command.

    This command uses `unittest.mock.patch` to intercept file system operations (`write_text`, `mkdir`)
    from the `explode` command. This allows us to reuse the exact logic of `explode` to determine
    which files *would* be created, without actually creating them or modifying the `explode` implementation
    to support a dry-run flag.
    """

    cwd = Path.cwd()

    if agent:
        agents_to_run = [agent]
    else:
        detected = detect_active_agents(cwd)
        if detected:
            log.info("detected active agents in target directory", detected=detected)
            if not print_output:
                typer.echo(f"Detected active agents: {', '.join(detected)}")
            agents_to_run = detected
        else:
            agents_to_run = ["all"]

    ignored_files = []

    def mock_write_text(self, data, encoding=None, errors=None):
        # Instead of writing to disk, we record the path that would have been written
        ignored_files.append(self)
        return len(data)

    def mock_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        # We suppress directory creation
        pass

    # Capture stdout/stderr to suppress explode output (logs, success messages)
    f_out = io.StringIO()
    f_err = io.StringIO()

    exit_exception = None

    try:
        # We patch Path.write_text and Path.mkdir to intercept file creation calls.
        # This is a creative way to "dry run" the explode command without refactoring it.
        with (
            patch(
                "pathlib.Path.write_text", autospec=True, side_effect=mock_write_text
            ),
            patch("pathlib.Path.mkdir", autospec=True, side_effect=mock_mkdir),
            redirect_stdout(f_out),
            redirect_stderr(f_err),
        ):
            for agent_name in agents_to_run:
                explode_implementation(input_file, agent_name, cwd)

    except typer.Exit as e:
        exit_exception = e

    if exit_exception and exit_exception.exit_code != 0:
        # If explode failed, print captured stderr to real stderr and re-raise
        print(f_err.getvalue(), file=sys.stderr)
        raise exit_exception

    # Process files to relative paths with forward slashes
    relative_files = []
    seen = set()
    for file_path in ignored_files:
        try:
            rel_path = file_path.relative_to(cwd).as_posix()
        except ValueError:
            rel_path = file_path.as_posix()

        if rel_path not in seen:
            seen.add(rel_path)
            relative_files.append(rel_path)

    # Sort files to ensure stable output
    relative_files.sort()

    if print_output:
        for f in relative_files:
            print(f)

        return

    # Update .gitignore
    gitignore_path = cwd / ".gitignore"
    gitignore_content = ""
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()

    start_marker = "# START AI INSTRUCTION IGNORES"
    end_marker = "# END AI INSTRUCTION IGNORES"

    ignores_block = f"{start_marker}\n"
    if relative_files:
        ignores_block += "\n".join(f"/{f}" for f in relative_files) + "\n"
    ignores_block += end_marker

    if start_marker in gitignore_content and end_marker in gitignore_content:
        # Replace existing block
        pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
        new_content = re.sub(pattern, ignores_block, gitignore_content, flags=re.DOTALL)
    else:
        # Append to end
        if gitignore_content and not gitignore_content.endswith("\n"):
            gitignore_content += "\n"

        new_content = gitignore_content
        if new_content:
            new_content += "\n"
        new_content += ignores_block + "\n"

    gitignore_path.write_text(new_content)
    typer.echo(f"Updated .gitignore with {len(relative_files)} ignored files.")
