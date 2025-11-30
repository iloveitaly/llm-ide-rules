"""Explode command: Convert instruction file to separate rule files."""

import os
from pathlib import Path
from typing_extensions import Annotated

import typer

from llm_ide_rules.agents import get_agent
from llm_ide_rules.log import log
from llm_ide_rules.agents.base import (
    trim_content,
    replace_header_with_proper_casing,
    write_rule_file,
)
from llm_ide_rules.constants import load_section_globs, header_to_filename, VALID_AGENTS


def extract_general(lines: list[str]) -> list[str]:
    """Extract lines before the first section header '## '."""
    general = []
    for line in lines:
        if line.startswith("## "):
            break
        general.append(line)
    return general


def extract_section(lines: list[str], header: str) -> list[str]:
    """Extract lines under a given section header until the next header or EOF.

    Includes the header itself in the output.
    """
    content = []
    in_section = False
    for line in lines:
        if in_section:
            if line.startswith("## "):
                break
            content.append(line)
        elif line.strip().lower() == header.lower():
            in_section = True
            content.append(line)
    return content


def extract_all_sections(lines: list[str]) -> dict[str, list[str]]:
    """Extract all sections from lines, returning dict of section_name -> content_lines."""
    sections = {}
    current_section = None
    current_content = []

    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections[current_section] = current_content

            current_section = line.strip()[3:]
            current_content = [line]
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = current_content

    return sections


def process_command_section(
    section_name: str,
    section_content: list[str],
    agents: list,
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
    cursor_agent,
    github_agent,
    cursor_rules_dir: Path,
    copilot_dir: Path,
) -> bool:
    """Process an unmapped section as an always-apply rule."""
    if not any(line.strip() for line in section_content):
        return False

    filename = header_to_filename(section_name)
    section_content = replace_header_with_proper_casing(section_content, section_name)

    cursor_agent.write_rule(section_content, filename, cursor_rules_dir, glob_pattern=None)
    github_agent.write_rule(section_content, filename, copilot_dir, glob_pattern=None)

    return True


def explode_main(
    input_file: Annotated[
        str, typer.Argument(help="Input markdown file")
    ] = "instructions.md",
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose logging")
    ] = False,
    config: Annotated[
        str, typer.Option("--config", "-c", help="Custom configuration file path")
    ] = None,
    agent: Annotated[
        str, typer.Option("--agent", "-a", help="Agent to explode for (cursor, github, claude, gemini, or all)")
    ] = "all",
):
    """Convert instruction file to separate rule files."""
    if verbose and "LOG_LEVEL" not in os.environ:
        os.environ["LOG_LEVEL"] = "DEBUG"

    if agent not in VALID_AGENTS:
        log.error("Invalid agent", agent=agent, valid_agents=VALID_AGENTS)
        typer.echo(f"Error: Invalid agent '{agent}'. Must be one of: {', '.join(VALID_AGENTS)}")
        raise typer.Exit(1)

    section_globs = load_section_globs(config)

    log.info("Starting explode operation", input_file=input_file, agent=agent, config=config)

    cwd = Path.cwd()

    # Initialize only the agents we need
    agents_to_process = []
    if agent == "all":
        agents_to_process = ["cursor", "github", "claude", "gemini"]
    else:
        agents_to_process = [agent]

    # Initialize agents and create directories
    agent_instances = {}
    agent_dirs = {}

    for agent_name in agents_to_process:
        agent_instances[agent_name] = get_agent(agent_name)

        if agent_name in ["cursor", "github"]:
            # These agents have both rules and commands
            rules_dir = cwd / agent_instances[agent_name].rules_dir
            commands_dir = cwd / agent_instances[agent_name].commands_dir
            rules_dir.mkdir(parents=True, exist_ok=True)
            commands_dir.mkdir(parents=True, exist_ok=True)
            agent_dirs[agent_name] = {"rules": rules_dir, "commands": commands_dir}
        else:
            # claude and gemini only have commands
            commands_dir = cwd / agent_instances[agent_name].commands_dir
            commands_dir.mkdir(parents=True, exist_ok=True)
            agent_dirs[agent_name] = {"commands": commands_dir}

    input_path = cwd / input_file

    try:
        lines = input_path.read_text().splitlines(keepends=True)
    except FileNotFoundError:
        log.error("Input file not found", input_file=str(input_path))
        raise typer.Exit(1)

    commands_path = input_path.parent / "commands.md"
    commands_lines = []
    if commands_path.exists():
        commands_lines = commands_path.read_text().splitlines(keepends=True)
        log.info("Found commands file", commands_file=str(commands_path))

    # Process general instructions for agents that support rules
    general = extract_general(lines)
    if any(line.strip() for line in general):
        general_header = """
---
description:
alwaysApply: true
---
"""
        if "cursor" in agent_instances:
            write_rule_file(agent_dirs["cursor"]["rules"] / "general.mdc", general_header, general)
        if "github" in agent_instances:
            agent_instances["github"].write_general_instructions(general, cwd)

    # Process mapped sections for agents that support rules
    found_sections = set()
    for section_name, glob_pattern in section_globs.items():
        section_content = extract_section(lines, f"## {section_name}")
        if any(line.strip() for line in section_content):
            found_sections.add(section_name)
            filename = header_to_filename(section_name)

            section_content = replace_header_with_proper_casing(
                section_content, section_name
            )

            if "cursor" in agent_instances:
                agent_instances["cursor"].write_rule(
                    section_content, filename, agent_dirs["cursor"]["rules"], glob_pattern
                )
            if "github" in agent_instances:
                agent_instances["github"].write_rule(
                    section_content, filename, agent_dirs["github"]["rules"], glob_pattern
                )

    for section_name in section_globs:
        if section_name not in found_sections:
            log.warning("Section not found in file", section=section_name)

    # Process unmapped sections for agents that support rules
    if "cursor" in agent_instances or "github" in agent_instances:
        for line in lines:
            if line.startswith("## "):
                section_name = line.strip()[3:]
                if not any(
                    section_name.lower() == mapped_section.lower()
                    for mapped_section in section_globs
                ):
                    log.warning(
                        "Unmapped section in instructions.md, treating as always-apply rule",
                        section=section_name,
                    )
                    section_content = extract_section(lines, f"## {section_name}")

                    if "cursor" in agent_instances and "github" in agent_instances:
                        process_unmapped_as_always_apply(
                            section_name,
                            section_content,
                            agent_instances["cursor"],
                            agent_instances["github"],
                            agent_dirs["cursor"]["rules"],
                            agent_dirs["github"]["rules"],
                        )
                    elif "cursor" in agent_instances:
                        # Only cursor - write just cursor rules
                        if any(line.strip() for line in section_content):
                            filename = header_to_filename(section_name)
                            section_content = replace_header_with_proper_casing(section_content, section_name)
                            agent_instances["cursor"].write_rule(
                                section_content, filename, agent_dirs["cursor"]["rules"], glob_pattern=None
                            )
                    elif "github" in agent_instances:
                        # Only github - write just github rules
                        if any(line.strip() for line in section_content):
                            filename = header_to_filename(section_name)
                            section_content = replace_header_with_proper_casing(section_content, section_name)
                            agent_instances["github"].write_rule(
                                section_content, filename, agent_dirs["github"]["rules"], glob_pattern=None
                            )

    # Process commands for all agents
    if commands_lines:
        command_sections = extract_all_sections(commands_lines)
        agents = [agent_instances[name] for name in agents_to_process]
        command_dirs = {name: agent_dirs[name]["commands"] for name in agents_to_process}

        for section_name, section_content in command_sections.items():
            process_command_section(section_name, section_content, agents, command_dirs)

    # Build log message and user output based on processed agents
    log_data = {"agent": agent}
    created_dirs = []

    for agent_name in agents_to_process:
        if agent_name in ["cursor", "github"]:
            log_data[f"{agent_name}_rules"] = str(agent_dirs[agent_name]["rules"])
            log_data[f"{agent_name}_commands"] = str(agent_dirs[agent_name]["commands"])
            created_dirs.append(f".{agent_name}/")
        else:
            log_data[f"{agent_name}_commands"] = str(agent_dirs[agent_name]["commands"])
            created_dirs.append(f".{agent_name}/")

    log.info("Explode operation completed", **log_data)

    if len(created_dirs) == 1:
        typer.echo(f"Created files in {created_dirs[0]} directory")
    else:
        typer.echo(f"Created files in {', '.join(created_dirs)} directories")
