"""LLM Rules CLI package for managing IDE prompts and rules."""

import typer
from typing_extensions import Annotated

from airules.commands.explode import explode_main
from airules.commands.implode import cursor, github
from airules.commands.download import download_main
from airules.commands.db_prompt import db_prompt_main

__version__ = "0.1.0"

app = typer.Typer(
    name="airules",
    help="CLI tool for managing LLM IDE prompts and rules",
    no_args_is_help=True,
)

# Add commands directly
app.command("explode", help="Convert instruction file to separate rule files")(explode_main)
app.command("download", help="Download LLM instruction files from GitHub repositories")(download_main)
app.command("db-prompt", help="Generate database schema prompts using llm-sql-prompt")(db_prompt_main)

# Create implode sub-typer
implode_app = typer.Typer(help="Bundle rule files into a single instruction file")
implode_app.command("cursor", help="Bundle Cursor rules into a single file")(cursor)
implode_app.command("github", help="Bundle GitHub/Copilot instructions into a single file")(github)
app.add_typer(implode_app, name="implode")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()