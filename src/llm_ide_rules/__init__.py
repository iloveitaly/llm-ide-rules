"""LLM Rules CLI package for managing IDE prompts and rules."""

import os

if "LOG_LEVEL" not in os.environ:
    os.environ["LOG_LEVEL"] = "WARNING"

import typer
from typing_extensions import Annotated

from llm_ide_rules.commands.explode import explode_main
from llm_ide_rules.commands.implode import cursor, github, claude, gemini, opencode
from llm_ide_rules.commands.download import download_main
from llm_ide_rules.commands.delete import delete_main
from llm_ide_rules.commands.config import config_main
from llm_ide_rules.commands.mcp import mcp_app

__version__ = "0.7.0"


def version_callback(value: bool):
    """Callback to display the version and exit."""
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
    """Global CLI options."""
    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
        import structlog_config

        structlog_config.configure_logger()


# Add commands directly
app.command("explode", help="Convert instruction file to separate rule files")(
    explode_main
)
app.command("download", help="Download LLM instruction files from GitHub repositories")(
    download_main
)
app.command("delete", help="Remove downloaded LLM instruction files")(delete_main)
app.command("config", help="Configure agents to use AGENTS.md")(config_main)

# Create implode sub-typer
implode_app = typer.Typer(help="Bundle rule files into a single instruction file")
implode_app.command(
    "cursor", help="Bundle Cursor rules and commands into a single file"
)(cursor)
implode_app.command(
    "github", help="Bundle GitHub/Copilot instructions and prompts into a single file"
)(github)
implode_app.command("claude", help="Bundle Claude Code commands into a single file")(
    claude
)
implode_app.command("gemini", help="Bundle Gemini CLI commands into a single file")(
    gemini
)
implode_app.command("opencode", help="Bundle OpenCode commands into a single file")(
    opencode
)
app.add_typer(implode_app, name="implode")

# Add MCP configuration management
app.add_typer(mcp_app, name="mcp")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
