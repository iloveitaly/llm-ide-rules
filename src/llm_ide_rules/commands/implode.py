"""Implode command: Bundle rule files into a single instruction file."""

from typing_extensions import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.log import log
from llm_ide_rules.utils import find_project_root


def cursor(
    output: Annotated[
        str, typer.Argument(help="Output file for rules")
    ] = "instructions.md",
) -> None:
    """Bundle Cursor rules into instructions.md and commands into commands.md."""

    agent = get_agent("cursor")
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("cursor rules directory not configured")
        raise typer.Exit(1)

    log.info(
        "bundling cursor rules and commands",
        rules_dir=rules_dir,
        commands_dir=agent.commands_dir,
    )

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error("cursor rules directory not found", rules_dir=str(rules_path))
        error_msg = f"Cursor rules directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    rules_written = agent.bundle_rules(output_path)
    if rules_written:
        success_msg = f"Bundled cursor rules into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no cursor rules to bundle")

    commands_output_path = base_dir / "commands.md"
    commands_written = agent.bundle_commands(commands_output_path)
    if commands_written:
        success_msg = "Bundled cursor commands into commands.md"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        commands_output_path.unlink(missing_ok=True)


def github(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    """Bundle GitHub instructions into instructions.md and prompts into commands.md."""

    agent = get_agent("github")
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("github rules directory not configured")
        raise typer.Exit(1)

    log.info(
        "bundling github instructions and prompts",
        instructions_dir=rules_dir,
        prompts_dir=agent.commands_dir,
    )

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error(
            "github instructions directory not found", instructions_dir=str(rules_path)
        )
        error_msg = f"GitHub instructions directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    instructions_written = agent.bundle_rules(output_path)
    if instructions_written:
        success_msg = f"Bundled github instructions into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no github instructions to bundle")

    commands_output_path = base_dir / "commands.md"
    prompts_written = agent.bundle_commands(commands_output_path)
    if prompts_written:
        success_msg = "Bundled github prompts into commands.md"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        commands_output_path.unlink(missing_ok=True)


def claude(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
) -> None:
    """Bundle Claude Code commands into commands.md."""

    agent = get_agent("claude")
    base_dir = find_project_root()

    commands_dir = agent.commands_dir
    if not commands_dir:
        log.error("claude code commands directory not configured")
        raise typer.Exit(1)

    log.info(
        "bundling claude code commands",
        commands_dir=commands_dir,
    )

    commands_path = base_dir / commands_dir
    if not commands_path.exists():
        log.error(
            "claude code commands directory not found", commands_dir=str(commands_path)
        )
        error_msg = f"Claude Code commands directory not found: {commands_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    commands_written = agent.bundle_commands(output_path)
    if commands_written:
        success_msg = f"Bundled claude commands into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no claude commands to bundle")


def gemini(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
) -> None:
    """Bundle Gemini CLI commands into commands.md."""

    agent = get_agent("gemini")
    base_dir = find_project_root()

    commands_dir = agent.commands_dir
    if not commands_dir:
        log.error("gemini cli commands directory not configured")
        raise typer.Exit(1)

    log.info(
        "bundling gemini cli commands",
        commands_dir=commands_dir,
    )

    commands_path = base_dir / commands_dir
    if not commands_path.exists():
        log.error(
            "gemini cli commands directory not found", commands_dir=str(commands_path)
        )
        error_msg = f"Gemini CLI commands directory not found: {commands_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    commands_written = agent.bundle_commands(output_path)
    if commands_written:
        success_msg = f"Bundled gemini commands into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no gemini commands to bundle")


def opencode(
    output: Annotated[str, typer.Argument(help="Output file")] = "commands.md",
) -> None:
    """Bundle OpenCode commands into commands.md."""

    agent = get_agent("opencode")
    base_dir = find_project_root()

    commands_dir = agent.commands_dir
    if not commands_dir:
        log.error("opencode commands directory not configured")
        raise typer.Exit(1)

    log.info(
        "bundling opencode commands",
        commands_dir=commands_dir,
    )

    commands_path = base_dir / commands_dir
    if not commands_path.exists():
        log.error(
            "opencode commands directory not found", commands_dir=str(commands_path)
        )
        error_msg = f"OpenCode commands directory not found: {commands_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    commands_written = agent.bundle_commands(output_path)
    if commands_written:
        success_msg = f"Bundled opencode commands into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no opencode commands to bundle")
