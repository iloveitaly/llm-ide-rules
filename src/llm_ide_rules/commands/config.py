"""Command to configure agents to use AGENTS.md."""

from pathlib import Path

import typer
from typing_extensions import Annotated

from llm_ide_rules.agents import get_agent, get_all_agents

def config_main(
    agent: Annotated[
        str, 
        typer.Option(help="Specific agent to configure (cursor, github, etc.)")
    ] = None,
):
    """
    Configure agents to use AGENTS.md as their context source.
    """
    base_dir = Path.cwd()
    
    agents_to_configure = []
    if agent:
        try:
            agents_to_configure.append(get_agent(agent))
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        agents_to_configure = get_all_agents()
        
    for agent_inst in agents_to_configure:
        if agent_inst.name == "agents":
            continue
            
        try:
            agent_inst.configure_agents_md(base_dir)
            typer.echo(f"Configured {agent_inst.name}")
        except Exception as e:
            typer.echo(f"Failed to configure {agent_inst.name}: {e}", err=True)

