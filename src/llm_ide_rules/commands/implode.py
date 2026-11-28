"implode command: bundle rule files into a single instruction file"

from typing import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.log import log
from llm_ide_rules.utils import find_project_root


def _bundle_agents_md(label: str, output: str = "instructions.md") -> bool:
    "bundle AGENTS.md files into instructions.md (or specified output)"
    agents_agent = get_agent("agents")
    base_dir = find_project_root()
    instructions_output_path = base_dir / output
    rules_written = agents_agent.bundle_rules(instructions_output_path)

    if rules_written:
        success_msg = f"Bundled {label} rules (AGENTS.md) into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
        return True

    log.info("no AGENTS.md files to bundle", provider=label)
    return False


def _require_agents_md(label: str, output: str) -> None:
    "bundle AGENTS.md and exit when that is the client's only instruction file"

    if _bundle_agents_md(label, output):
        return

    error_msg = f"No {label} AGENTS.md files found to bundle"
    typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
    raise typer.Exit(1)


def cursor(
    output: Annotated[
        str, typer.Argument(help="Output file for rules")
    ] = "instructions.md",
) -> None:
    "bundle Cursor rules into instructions.md"

    agent = get_agent("cursor")
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("cursor rules directory not configured")
        raise typer.Exit(1)

    log.info("bundling cursor rules", rules_dir=rules_dir)

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error("cursor rules directory not found", rules_dir=rules_path)
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


def github(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle GitHub instructions into instructions.md"

    agent = get_agent("github")
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("github rules directory not configured")
        raise typer.Exit(1)

    log.info("bundling github instructions", instructions_dir=rules_dir)

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error(
            "github instructions directory not found", instructions_dir=rules_path
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


def claude(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle Claude Code rules into instructions.md"

    agent = get_agent("claude")
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("claude code rules directory not configured")
        raise typer.Exit(1)

    log.info("bundling claude code rules", rules_dir=rules_dir)

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error("claude code rules directory not found", rules_dir=rules_path)
        error_msg = f"Claude Code rules directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    instructions_written = agent.bundle_rules(output_path)
    if instructions_written:
        success_msg = f"Bundled claude rules into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no claude rules to bundle")


def _bundle_dot_agents(
    output: str = "instructions.md",
    label: str = "grok",
) -> None:
    "shared implementation for .agents layout providers (grok)"

    agent = get_agent(label)
    base_dir = find_project_root()

    rules_dir = agent.rules_dir
    if not rules_dir:
        log.error("rules directory not configured", provider=label)
        raise typer.Exit(1)

    log.info("bundling rules", provider=label, rules_dir=rules_dir)

    rules_path = base_dir / rules_dir
    if not rules_path.exists():
        log.error("rules directory not found", provider=label, rules_dir=rules_path)
        error_msg = f"{label.title()} rules directory not found: {rules_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    output_path = base_dir / output
    instructions_written = agent.bundle_rules(output_path)
    if instructions_written:
        success_msg = f"Bundled {label} rules into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no rules to bundle", provider=label)


def antigravity(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle Antigravity AGENTS.md into instructions.md"

    _require_agents_md("Antigravity", output)


def grok(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle Grok (.agents) rules into instructions.md"
    _bundle_dot_agents(output, "grok")


def agents(
    output: Annotated[
        str, typer.Argument(help="Output file for rules")
    ] = "instructions.md",
    filename: Annotated[
        str,
        typer.Option("--filename", "-f", help="Filename to bundle (e.g. AGENTS.md)"),
    ] = "AGENTS.md",
) -> None:
    "bundle unified markdown files (default AGENTS.md) into instructions.md"

    agent = get_agent("agents")
    base_dir = find_project_root()

    log.info("bundling files", filename=filename)

    output_path = base_dir / output
    rules_written = agent.bundle_rules(output_path, filename=filename)
    if rules_written:
        success_msg = f"Bundled {filename} files into {output}"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        output_path.unlink(missing_ok=True)
        log.info("no files to bundle", filename=filename)


def opencode(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle OpenCode AGENTS.md into instructions.md"

    _require_agents_md("OpenCode", output)


def codex(
    output: Annotated[
        str, typer.Argument(help="Output file for instructions")
    ] = "instructions.md",
) -> None:
    "bundle Codex AGENTS.md into instructions.md"

    _require_agents_md("Codex", output)
