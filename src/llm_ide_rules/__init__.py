"LLM Rules CLI package for managing IDE prompts and rules"

import os

if "LOG_LEVEL" not in os.environ:
    os.environ["LOG_LEVEL"] = "WARNING"

from typing import Annotated

import typer

from llm_ide_rules.commands.config import config_main
from llm_ide_rules.commands.delete import delete_main
from llm_ide_rules.commands.download import download_main
from llm_ide_rules.commands.explode import explode_main
from llm_ide_rules.commands.exploded import exploded_main
from llm_ide_rules.commands.ignores import ignores_main
from llm_ide_rules.commands.implode import (
    agents,
    antigravity,
    claude,
    codex,
    cursor,
    github,
    grok,
    opencode,
)
from llm_ide_rules.version import __version__


def version_callback(value: bool):
    "callback to display the version and exit"

    if value:
        print(f"llm-ide-rules version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="llm_ide_rules",
    help="CLI tool for managing LLM IDE prompts and rules",
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Enable verbose logging (sets LOG_LEVEL=DEBUG)"
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            help="Show the version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
):
    "global CLI options"

    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
        import structlog_config

        structlog_config.configure_logger()


# add commands directly
app.command("explode", help="Convert instruction file to separate rule files")(
    explode_main
)
app.command("exploded", help="List clients that were exploded")(exploded_main)
app.command("ignores", help="Generate list of files to ignore based on instructions")(
    ignores_main
)
app.command("download", help="Download LLM instruction files from GitHub repositories")(
    download_main
)
app.command("delete", help="Remove downloaded LLM instruction files")(delete_main)
app.command("config", help="Configure agents to use AGENTS.md")(config_main)

# create implode sub-typer
implode_app = typer.Typer(help="Bundle rule files into a single instruction file")
implode_app.command(
    "cursor", help="Bundle Cursor rules and commands into a single file"
)(cursor)
implode_app.command(
    "github", help="Bundle GitHub/Copilot instructions and prompts into a single file"
)(github)
implode_app.command(
    "claude", help="Bundle Claude Code rules and commands into single files"
)(claude)
implode_app.command(
    "antigravity",
    help="Bundle Antigravity skills and AGENTS.md into single files",
)(antigravity)
implode_app.command(
    "grok", help="Bundle Grok (.agents) rules and skills into single files"
)(grok)
implode_app.command("opencode", help="Bundle OpenCode commands into a single file")(
    opencode
)
implode_app.command(
    "codex", help="Bundle Codex skills and AGENTS.md into single files"
)(codex)
implode_app.command("agents", help="Bundle AGENTS.md files into a single file")(agents)
app.add_typer(implode_app, name="implode")


def main():
    "main entry point for the CLI"

    app()


if __name__ == "__main__":
    main()
