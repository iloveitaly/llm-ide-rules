"""Main CLI entry point for llm-rules."""

import typer
from typing_extensions import Annotated

from llm_rules.commands.explode import explode_main
from llm_rules.commands.implode import cursor, github, implode_main
from llm_rules.commands.mcp import status, configure

app = typer.Typer(
    name="llm-rules",
    help="CLI tool for managing LLM IDE prompts and rules",
    no_args_is_help=True,
)

# Add commands directly
app.command("explode", help="Convert instruction file to separate rule files")(explode_main)

# Create implode sub-typer
implode_app = typer.Typer(help="Bundle rule files into a single instruction file")
implode_app.command("cursor", help="Bundle Cursor rules into a single file")(cursor)
implode_app.command("github", help="Bundle GitHub/Copilot instructions into a single file")(github)
implode_app.callback(invoke_without_command=True)(implode_main)
app.add_typer(implode_app, name="implode")

# Create mcp sub-typer
mcp_app = typer.Typer(help="MCP (Model Context Protocol) related commands")
mcp_app.command("status")(status)
mcp_app.command("configure")(configure)
app.add_typer(mcp_app, name="mcp")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()