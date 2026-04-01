"""Explode command: Convert instruction file to separate rule files."""

from pathlib import Path
from typing_extensions import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.agents.base import (
    BaseAgent,
    replace_header_with_proper_casing,
    write_rule_file,
)
from llm_ide_rules.log import log
from llm_ide_rules.constants import header_to_filename, VALID_AGENTS
from llm_ide_rules.markdown_parser import parse_sections


def process_command_section(
    section_name: str,
    section_content: list[str],
    agents: list[BaseAgent],
    dirs: dict[str, Path],
) -> bool:
    """Process a section as a command for all agents."""
    if not any(line.strip() for line in section_content):
        return False

    filename = header_to_filename(section_name)
    section_content = replace_header_with_proper_casing(section_content, section_name)

    for agent in agents:
        if agent.commands_dir:
            agent.write_command(
                section_content, filename, dirs[agent.name], section_name
            )

    return True


def process_unmapped_as_always_apply(
    section_name: str,
    section_content: list[str],
    rule_agents: list[tuple[BaseAgent, Path]],
) -> bool:
    """Process an unmapped section as an always-apply rule."""
    if not any(line.strip() for line in section_content):
        return False

    filename = header_to_filename(section_name)
    section_content = replace_header_with_proper_casing(section_content, section_name)

    for agent, rules_dir in rule_agents:
        agent.write_rule(
            section_content,
            filename,
            rules_dir,
            glob_pattern=None,
            description=section_name,
        )

    return True


def get_always_apply_rule_agents(
    agent_instances: dict[str, BaseAgent], agent_dirs: dict[str, dict[str, Path]]
) -> list[tuple[BaseAgent, Path]]:
    """Return rule-capable agents that should receive always-apply sections."""
    if "agents" in agent_instances:
        eligible_agent_names = ["claude"]
    else:
        eligible_agent_names = [
            agent_name
            for agent_name in agent_instances
            if "rules" in agent_dirs[agent_name]
        ]

    return [
        (agent_instances[agent_name], agent_dirs[agent_name]["rules"])
        for agent_name in eligible_agent_names
        if agent_name in agent_instances and "rules" in agent_dirs[agent_name]
    ]


def explode_implementation(
    input_file: str = "instructions.md",
    agent: str = "all",
    working_dir: Path | None = None,
) -> None:
    """Core implementation of explode command."""
    if working_dir is None:
        working_dir = Path.cwd()

    if agent not in VALID_AGENTS:
        log.error("invalid agent", agent=agent, valid_agents=VALID_AGENTS)
        error_msg = (
            f"Invalid agent '{agent}'. Must be one of: {', '.join(VALID_AGENTS)}"
        )
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    log.info(
        "starting explode operation",
        input_file=input_file,
        agent=agent,
        working_dir=str(working_dir),
    )

    # Initialize only the agents we need
    agents_to_process = []
    if agent == "all":
        agents_to_process = [
            "cursor",
            "github",
            "claude",
            "gemini",
            "opencode",
            "agents",
        ]
    else:
        agents_to_process = [agent]
        # OpenCode and Gemini use AGENTS.md, so enable the agents adapter automatically
        if agent in ["opencode", "gemini"] and "agents" not in agents_to_process:
            agents_to_process.append("agents")

    # Initialize agents and create directories
    agent_instances = {}
    agent_dirs = {}

    for agent_name in agents_to_process:
        agent_instances[agent_name] = get_agent(agent_name)
        current_agent = agent_instances[agent_name]

        agent_dir_map = {}
        if current_agent.rules_dir:
            agent_dir_map["rules"] = working_dir / current_agent.rules_dir
        if current_agent.commands_dir:
            agent_dir_map["commands"] = working_dir / current_agent.commands_dir

        agent_dirs[agent_name] = agent_dir_map

    input_path = working_dir / input_file

    try:
        input_text = input_path.read_text()
        
        # Strip marker and everything after it if present
        marker = "<!-- END CLONED INSTRUCTIONS -->"
        if marker in input_text:
            log.info("ignoring content after marker in instructions file", marker=marker)
            input_text = input_text.split(marker, 1)[0]
    except FileNotFoundError:
        log.error("input file not found", input_file=str(input_path))
        error_msg = f"Input file not found: {input_path}"
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    commands_path = input_path.parent / "commands.md"
    commands_text = ""
    if commands_path.exists():
        commands_text = commands_path.read_text()
        log.info("found commands file", commands_file=str(commands_path))
        
        # Also strip marker for commands.md
        if marker in commands_text:
            log.info("ignoring content after marker in commands file", marker=marker)
            commands_text = commands_text.split(marker, 1)[0]

    # Parse instructions
    general, instruction_sections = parse_sections(input_text)

    # Process general instructions for agents that support rules
    if any(line.strip() for line in general):
        general_header = """
---
description: General Instructions
globs: 
alwaysApply: true
---
"""
        if "cursor" in agent_instances:
            write_rule_file(
                agent_dirs["cursor"]["rules"] / "general.mdc", general_header, general
            )
        if "github" in agent_instances:
            agent_instances["github"].write_general_instructions(general, working_dir)
        if "claude" in agent_instances:
            agent_instances["claude"].write_rule(
                general,
                "general",
                agent_dirs["claude"]["rules"],
                glob_pattern=None,
                description="General Instructions",
            )

    # Process sections for agents that support rules
    rules_sections: dict[str, list[str]] = {}
    section_globs: dict[str, str | None] = {}

    for section_name, section_data in instruction_sections.items():
        content = section_data.content
        glob_pattern = section_data.glob_pattern

        if not any(line.strip() for line in content):
            continue

        rules_sections[section_name] = content
        section_globs[section_name] = glob_pattern
        filename = header_to_filename(section_name)

        section_content = replace_header_with_proper_casing(content, section_name)

        if glob_pattern is None:
            # No directive = alwaysApply
            rule_agents = get_always_apply_rule_agents(agent_instances, agent_dirs)

            if rule_agents:
                process_unmapped_as_always_apply(
                    section_name,
                    section_content,
                    rule_agents,
                )
        elif glob_pattern != "manual":
            # Has glob pattern = file-specific rule
            for agent_name in agent_instances:
                if "rules" not in agent_dirs[agent_name]:
                    continue

                agent_instances[agent_name].write_rule(
                    section_content,
                    filename,
                    agent_dirs[agent_name]["rules"],
                    glob_pattern,
                    description=section_name,
                )

    # Process commands for all agents
    command_sections_data = {}
    command_sections = {}
    if commands_text:
        _, command_sections_data = parse_sections(commands_text)
        agents_with_commands = [
            agent_instances[name]
            for name in agents_to_process
            if agent_instances[name].commands_dir
        ]
        command_dirs = {
            name: agent_dirs[name]["commands"]
            for name in agents_to_process
            if "commands" in agent_dirs[name]
        }

        for section_name, section_data in command_sections_data.items():
            command_sections[section_name] = section_data.content
            process_command_section(
                section_name, section_data.content, agents_with_commands, command_dirs
            )

    # Generate root documentation for agents that support it
    for agent_name, agent_inst in agent_instances.items():
        agent_inst.generate_root_doc(
            general,
            rules_sections,
            command_sections,
            working_dir,
            section_globs=section_globs,
        )

    # Build log message and user output based on processed agents
    log_data = {"agent": agent}
    created_dirs = []

    for agent_name in agents_to_process:
        if "rules" in agent_dirs[agent_name]:
            log_data[f"{agent_name}_rules"] = str(agent_dirs[agent_name]["rules"])
        if "commands" in agent_dirs[agent_name]:
            log_data[f"{agent_name}_commands"] = str(agent_dirs[agent_name]["commands"])
        if agent_dirs[agent_name]:
            created_dirs.append(f".{agent_name}/")
        # else: agent has no directories (e.g., agents which only generates root doc)

    created_dirs = list(dict.fromkeys(created_dirs))

    if "gemini" in agent_instances:
        if not agent_instances["gemini"].check_agents_md_config(working_dir):
            typer.secho(
                "Warning: Gemini CLI configuration missing for AGENTS.md.",
                fg=typer.colors.YELLOW,
            )
            typer.secho(
                "Run this command to configure it:",
                fg=typer.colors.YELLOW,
            )
            typer.secho(
                "  llm-ide-rules config",
                fg=typer.colors.YELLOW,
            )

    if created_dirs:
        if len(created_dirs) == 1:
            success_msg = f"Created files in {created_dirs[0]} directory"
            typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
        else:
            success_msg = f"Created files in {', '.join(created_dirs)} directories"
            typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        # No directories created (e.g., agents that only generate root docs)
        success_msg = "Created root documentation files"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))


def explode_main(
    input_file: Annotated[
        str, typer.Argument(help="Input markdown file")
    ] = "instructions.md",
    agent: Annotated[
        str,
        typer.Option(
            "--agent",
            "-a",
            help="Agent to explode for (cursor, github, claude, gemini, or all)",
        ),
    ] = "all",
) -> None:
    """Convert instruction file to separate rule files."""
    explode_implementation(input_file, agent, Path.cwd())
