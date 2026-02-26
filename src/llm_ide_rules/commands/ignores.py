import typer
from pathlib import Path
from typing_extensions import Annotated
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr
import io
import sys

from llm_ide_rules.commands.explode import explode_implementation


def ignores_main(
    input_file: Annotated[
        str, typer.Argument(help="Input markdown file")
    ] = "instructions.md",
    agent: Annotated[
        str,
        typer.Option(
            "--agent",
            "-a",
            help="Agent to list ignores for (cursor, github, claude, gemini, or all)",
        ),
    ] = "all",
) -> None:
    """Generate a list of files that should be ignored by dry-running the explode command.

    This command uses `unittest.mock.patch` to intercept file system operations (`write_text`, `mkdir`)
    from the `explode` command. This allows us to reuse the exact logic of `explode` to determine
    which files *would* be created, without actually creating them or modifying the `explode` implementation
    to support a dry-run flag.
    """

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
        with patch("pathlib.Path.write_text", autospec=True, side_effect=mock_write_text), \
             patch("pathlib.Path.mkdir", autospec=True, side_effect=mock_mkdir), \
             redirect_stdout(f_out), \
             redirect_stderr(f_err):

            explode_implementation(input_file, agent, Path.cwd())

    except typer.Exit as e:
        exit_exception = e

    if exit_exception and exit_exception.exit_code != 0:
        # If explode failed, print captured stderr to real stderr and re-raise
        print(f_err.getvalue(), file=sys.stderr)
        raise exit_exception

    # Print the files relative to CWD
    cwd = Path.cwd()
    for file_path in ignored_files:
        try:
            print(file_path.relative_to(cwd))
        except ValueError:
            print(file_path)
