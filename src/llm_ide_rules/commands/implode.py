"""Implode command: Bundle rule files into a single instruction file."""

import logging
from pathlib import Path
from typing_extensions import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.constants import load_section_globs
from llm_ide_rules.log import log


def cursor(
    output: Annotated[str, typer.Argument(help="Output file for rules")] = "instructions.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
    config: Annotated[str, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
):
    """Bundle Cursor rules into instructions.md and commands into commands.md."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    section_globs = load_section_globs(config)
    agent = get_agent("cursor")
    cwd = Path.cwd()

    log.info(
        "Bundling Cursor rules and commands",
        rules_dir=agent.rules_dir,
        commands_dir=agent.commands_dir,
        config=config,
    )

    rules_path = cwd / agent.rules_dir
    if not rules_path.exists():
        log.error("Cursor rules directory not found", rules_dir=str(rules_path))
        raise typer.Exit(1)

    output_path = cwd / output
    rules_written = agent.bundle_rules(output_path, section_globs)
    if rules_written:
        log.info("Cursor rules bundled", output_file=str(output_path))
        typer.echo(f"Bundled cursor rules into {output}")
    else:
        output_path.unlink(missing_ok=True)
        log.info("No cursor rules to bundle")

    commands_output_path = cwd / "commands.md"
    commands_written = agent.bundle_commands(commands_output_path, section_globs)
    if commands_written:
        log.info("Cursor commands bundled", output_file=str(commands_output_path))
        typer.echo("Bundled cursor commands into commands.md")
    else:
        commands_output_path.unlink(missing_ok=True)


def github(
    output: Annotated[str, typer.Argument(help="Output file for instructions")] = "instructions.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
    config: Annotated[str, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
):
    """Bundle GitHub instructions into instructions.md and prompts into commands.md."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    section_globs = load_section_globs(config)
    agent = get_agent("github")
    cwd = Path.cwd()

    log.info(
        "Bundling GitHub instructions and prompts",
        instructions_dir=agent.rules_dir,
        prompts_dir=agent.commands_dir,
        config=config,
    )

    rules_path = cwd / agent.rules_dir
    if not rules_path.exists():
        log.error("GitHub instructions directory not found", instructions_dir=str(rules_path))
        raise typer.Exit(1)

    output_path = cwd / output
    instructions_written = agent.bundle_rules(output_path, section_globs)
    if instructions_written:
        log.info("GitHub instructions bundled", output_file=str(output_path))
        typer.echo(f"Bundled github instructions into {output}")
    else:
        output_path.unlink(missing_ok=True)
        log.info("No github instructions to bundle")

    commands_output_path = cwd / "commands.md"
    prompts_written = agent.bundle_commands(commands_output_path, section_globs)
    if prompts_written:
        log.info("GitHub prompts bundled", output_file=str(commands_output_path))
        typer.echo("Bundled github prompts into commands.md")
    else:
        commands_output_path.unlink(missing_ok=True)


def claude(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
    config: Annotated[str, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
):
    """Bundle Claude Code commands into commands.md."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    section_globs = load_section_globs(config)
    agent = get_agent("claude")
    cwd = Path.cwd()

    log.info(
        "Bundling Claude Code commands",
        commands_dir=agent.commands_dir,
        config=config,
    )

    commands_path = cwd / agent.commands_dir
    if not commands_path.exists():
        log.error("Claude Code commands directory not found", commands_dir=str(commands_path))
        raise typer.Exit(1)

    output_path = cwd / output
    commands_written = agent.bundle_commands(output_path, section_globs)
    if commands_written:
        log.info("Claude Code commands bundled successfully", output_file=str(output_path))
        typer.echo(f"Bundled claude commands into {output}")
    else:
        output_path.unlink(missing_ok=True)
        log.info("No claude commands to bundle")


def gemini(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
    config: Annotated[str, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
):
    """Bundle Gemini CLI commands into commands.md."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    section_globs = load_section_globs(config)
    agent = get_agent("gemini")
    cwd = Path.cwd()

    log.info(
        "Bundling Gemini CLI commands",
        commands_dir=agent.commands_dir,
        config=config,
    )

    commands_path = cwd / agent.commands_dir
    if not commands_path.exists():
        log.error("Gemini CLI commands directory not found", commands_dir=str(commands_path))
        raise typer.Exit(1)

    output_path = cwd / output
    commands_written = agent.bundle_commands(output_path, section_globs)
    if commands_written:
        log.info("Gemini CLI commands bundled successfully", output_file=str(output_path))
        typer.echo(f"Bundled gemini commands into {output}")
    else:
        output_path.unlink(missing_ok=True)
        log.info("No gemini commands to bundle")
