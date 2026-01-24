"""Implode command: Bundle rule files into a single instruction file."""

from pathlib import Path
from typing_extensions import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.constants import load_section_globs
from llm_ide_rules.log import log


def cursor(
    output: Annotated[str, typer.Argument(help="Output file for rules")] = "instructions.md",
    config: Annotated[str | None, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
) -> None:
    """Bundle Cursor rules into instructions.md and commands into commands.md."""

    section_globs = load_section_globs(config)
    agent = get_agent("cursor")
    cwd = Path.cwd()

    log.info(
        "bundling cursor rules and commands",
        rules_dir=agent.rules_dir,
        commands_dir=agent.commands_dir,
        config=config,
    )

    rules_path = cwd / agent.rules_dir
    if not rules_path.exists():
        log.error("cursor rules directory not found", rules_dir=str(rules_path))
        error_msg = f"Cursor rules directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = cwd / output
    rules_written = agent.bundle_rules(output_path, section_globs)
    if rules_written:
        success_msg = f"Bundled cursor rules into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no cursor rules to bundle")

    commands_output_path = cwd / "commands.md"
    commands_written = agent.bundle_commands(commands_output_path, section_globs)
    if commands_written:
        success_msg = "Bundled cursor commands into commands.md"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        commands_output_path.unlink(missing_ok=True)


def github(
    output: Annotated[str, typer.Argument(help="Output file for instructions")] = "instructions.md",
    config: Annotated[str | None, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
) -> None:
    """Bundle GitHub instructions into instructions.md and prompts into commands.md."""

    section_globs = load_section_globs(config)
    agent = get_agent("github")
    cwd = Path.cwd()

    log.info(
        "bundling github instructions and prompts",
        instructions_dir=agent.rules_dir,
        prompts_dir=agent.commands_dir,
        config=config,
    )

    rules_path = cwd / agent.rules_dir
    if not rules_path.exists():
        log.error("github instructions directory not found", instructions_dir=str(rules_path))
        error_msg = f"GitHub instructions directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = cwd / output
    instructions_written = agent.bundle_rules(output_path, section_globs)
    if instructions_written:
        success_msg = f"Bundled github instructions into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no github instructions to bundle")

    commands_output_path = cwd / "commands.md"
    prompts_written = agent.bundle_commands(commands_output_path, section_globs)
    if prompts_written:
        success_msg = "Bundled github prompts into commands.md"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        commands_output_path.unlink(missing_ok=True)


def claude(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
    config: Annotated[str | None, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
) -> None:
    """Bundle Claude Code commands into commands.md."""

    section_globs = load_section_globs(config)
    agent = get_agent("claude")
    cwd = Path.cwd()

    log.info(
        "bundling claude code commands",
        commands_dir=agent.commands_dir,
        config=config,
    )

    commands_path = cwd / agent.commands_dir
    if not commands_path.exists():
        log.error("claude code commands directory not found", commands_dir=str(commands_path))
        error_msg = f"Claude Code commands directory not found: {commands_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = cwd / output
    commands_written = agent.bundle_commands(output_path, section_globs)
    if commands_written:
        success_msg = f"Bundled claude commands into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no claude commands to bundle")


def gemini(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
    config: Annotated[str | None, typer.Option("--config", "-c", help="Custom configuration file path")] = None,
) -> None:
    """Bundle Gemini CLI commands into commands.md."""

    section_globs = load_section_globs(config)
    agent = get_agent("gemini")
    cwd = Path.cwd()

    log.info(
        "bundling gemini cli commands",
        commands_dir=agent.commands_dir,
        config=config,
    )

    commands_path = cwd / agent.commands_dir
    if not commands_path.exists():
        log.error("gemini cli commands directory not found", commands_dir=str(commands_path))
        error_msg = f"Gemini CLI commands directory not found: {commands_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = cwd / output
    commands_written = agent.bundle_commands(output_path, section_globs)
    if commands_written:
        success_msg = f"Bundled gemini commands into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no gemini commands to bundle")
