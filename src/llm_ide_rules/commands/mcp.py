"""
MCP configuration management commands.
"""

import json5
import typer
from pathlib import Path

from llm_ide_rules.agents import get_agent, get_all_agents
from llm_ide_rules.mcp import McpConfig
from llm_ide_rules.log import log

mcp_app = typer.Typer(help="MCP configuration management")


@mcp_app.command()
def explode(
    input_file: str = typer.Argument("mcp.json", help="Input unified MCP config file"),
    scope: str = typer.Option(
        "project", "--scope", "-s", help="Scope: project, global, or both"
    ),
    agent: str = typer.Option(
        "all",
        "--agent",
        "-a",
        help="Agent: claude, cursor, gemini, opencode, copilot, or all",
    ),
) -> None:
    """Convert unified mcp.json to platform-specific configs."""
    input_path = Path(input_file)
    if not input_path.exists():
        log.error("input file not found", file=input_file)
        raise typer.Exit(1)

    config = McpConfig.model_validate(json5.loads(input_path.read_text()))

    if agent == "all":
        agents = get_all_agents()
    else:
        agents = [get_agent(agent)]

    for ag in agents:
        if not ag.mcp_project_path:
            continue

        servers = {
            name: ag.transform_mcp_server(s) for name, s in config.servers.items()
        }

        if scope in ("project", "both"):
            project_path = Path.cwd() / ag.mcp_project_path
            ag.write_mcp_config(servers, project_path)
            log.info("wrote project config", agent=ag.name, path=str(project_path))

        if scope in ("global", "both"):
            global_path = Path.home() / ag.mcp_global_path
            ag.write_mcp_config(servers, global_path)
            log.info("wrote global config", agent=ag.name, path=str(global_path))


@mcp_app.command()
def implode(
    output_file: str = typer.Argument(
        "mcp.json", help="Output unified MCP config file"
    ),
    source: str = typer.Option(
        None, "--source", help="Source agent to read from (e.g., claude, cursor)"
    ),
    scope: str = typer.Option(
        "project", "--scope", "-s", help="Scope: project or global"
    ),
) -> None:
    """Merge platform-specific MCP configs into unified mcp.json."""
    if not source:
        log.error("source agent must be specified")
        raise typer.Exit(1)

    ag = get_agent(source)

    if scope == "project":
        source_path = Path.cwd() / ag.mcp_project_path
    else:
        source_path = Path.home() / ag.mcp_global_path

    if not source_path.exists():
        log.error("source config not found", path=str(source_path))
        raise typer.Exit(1)

    server_configs = ag.read_mcp_config(source_path)
    if not server_configs:
        log.error("no MCP servers found in config", path=str(source_path))
        raise typer.Exit(1)

    servers = {
        name: ag.reverse_transform_mcp_server(name, config)
        for name, config in server_configs.items()
    }

    config = McpConfig(servers=servers)
    output_path = Path(output_file)

    import json

    output_path.write_text(
        json.dumps(
            config.model_dump(exclude_none=True, exclude_defaults=True), indent=2
        )
    )
    log.info("wrote unified config", path=str(output_path))
