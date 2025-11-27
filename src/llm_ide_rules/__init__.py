"""LLM Rules CLI package for managing IDE prompts and rules."""

import typer
from typing_extensions import Annotated

from llm_ide_rules.commands.explode import explode_main
from llm_ide_rules.commands.implode import cursor, github, claude, gemini
from llm_ide_rules.commands.download import download_main
from llm_ide_rules.commands.delete import delete_main

__version__ = "0.4.0"

app = typer.Typer(
    name="llm_ide_rules",
    help="CLI tool for managing LLM IDE prompts and rules",
    no_args_is_help=True,
)

# Add commands directly
app.command("explode", help="Convert instruction file to separate rule files")(explode_main)
app.command("download", help="Download LLM instruction files from GitHub repositories")(download_main)
app.command("delete", help="Remove downloaded LLM instruction files")(delete_main)

# Create implode sub-typer
implode_app = typer.Typer(help="Bundle rule files into a single instruction file")
implode_app.command("cursor", help="Bundle Cursor rules and commands into a single file")(cursor)
implode_app.command("github", help="Bundle GitHub/Copilot instructions and prompts into a single file")(github)
implode_app.command("claude", help="Bundle Claude Code commands into a single file")(claude)
implode_app.command("gemini", help="Bundle Gemini CLI commands into a single file")(gemini)
app.add_typer(implode_app, name="implode")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()