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
from llm_ide_rules.constants import load_section_globs, header_to_filename, VALID_AGENTS
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

    cursor_agent.write_rule(
        section_content, filename, cursor_rules_dir, glob_pattern=None
    )
    github_agent.write_rule(section_content, filename, copilot_dir, glob_pattern=None)

    return True


def explode_main(
    input_file: Annotated[
        str, typer.Argument(help="Input markdown file")
    ] = "instructions.md",
    config: Annotated[
        str | None,
        typer.Option("--config", "-c", help="Custom configuration file path"),
    ] = None,
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

    if agent not in VALID_AGENTS:
        log.error("invalid agent", agent=agent, valid_agents=VALID_AGENTS)
        error_msg = (
            f"Invalid agent '{agent}'. Must be one of: {', '.join(VALID_AGENTS)}"
        )
        typer.echo(typer.style(error_msg, fg=typer.colors.RED), err=True)
        raise typer.Exit(1)

    section_globs = load_section_globs(config)

    log.info(
        "starting explode operation", input_file=input_file, agent=agent, config=config
    )

    cwd = Path.cwd()

    # Initialize only the agents we need
    agents_to_process = []
    if agent == "all":
        agents_to_process = ["cursor", "github", "claude", "gemini", "opencode"]
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
            # claude, gemini, and opencode only have commands
            commands_dir = cwd / agent_instances[agent_name].commands_dir
            commands_dir.mkdir(parents=True, exist_ok=True)
            agent_dirs[agent_name] = {"commands": commands_dir}

    input_path = cwd / input_file

    try:
        input_text = input_path.read_text()
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

    # Parse instructions
    general, instruction_sections = parse_sections(input_text)

    # Process general instructions for agents that support rules
    if any(line.strip() for line in general):
        general_header = """
---
description:
alwaysApply: true
---
"""
        if "cursor" in agent_instances:
            write_rule_file(
                agent_dirs["cursor"]["rules"] / "general.mdc", general_header, general
            )
        if "github" in agent_instances:
            agent_instances["github"].write_general_instructions(general, cwd)

    # Process mapped sections for agents that support rules
    found_sections = set()
    rules_sections: dict[str, list[str]] = {}

    for section_name, glob_pattern in section_globs.items():
        # Look for section (case-insensitive search in parsed sections)
        matched_section_content = None
        for parsed_header, content in instruction_sections.items():
            if parsed_header.lower() == section_name.lower():
                matched_section_content = content
                break
        
        if matched_section_content and any(line.strip() for line in matched_section_content):
            found_sections.add(section_name)
            rules_sections[section_name] = matched_section_content
            filename = header_to_filename(section_name)

            section_content = replace_header_with_proper_casing(
                matched_section_content, section_name
            )

            if "cursor" in agent_instances:
                agent_instances["cursor"].write_rule(
                    section_content,
                    filename,
                    agent_dirs["cursor"]["rules"],
                    glob_pattern,
                )
            if "github" in agent_instances:
                agent_instances["github"].write_rule(
                    section_content,
                    filename,
                    agent_dirs["github"]["rules"],
                    glob_pattern,
                )

    for section_name in section_globs:
        if section_name not in found_sections:
            log.warning("section not found in file", section=section_name)

    # Process unmapped sections for agents that support rules
    for parsed_header, content in instruction_sections.items():
        # Check if this header was already processed as a mapped section
        is_mapped = False
        for section_name in section_globs:
            if parsed_header.lower() == section_name.lower():
                is_mapped = True
                break
        
        if not is_mapped:
            log.warning(
                "unmapped section in instructions.md, treating as always-apply rule",
                section=parsed_header,
            )
            if any(line.strip() for line in content):
                rules_sections[parsed_header] = content

                if "cursor" in agent_instances and "github" in agent_instances:
                    process_unmapped_as_always_apply(
                        parsed_header,
                        content,
                        agent_instances["cursor"],
                        agent_instances["github"],
                        agent_dirs["cursor"]["rules"],
                        agent_dirs["github"]["rules"],
                    )
                elif "cursor" in agent_instances:
                    # Only cursor - write just cursor rules
                    filename = header_to_filename(parsed_header)
                    section_content = replace_header_with_proper_casing(
                        content, parsed_header
                    )
                    agent_instances["cursor"].write_rule(
                        section_content,
                        filename,
                        agent_dirs["cursor"]["rules"],
                        glob_pattern=None,
                    )
                elif "github" in agent_instances:
                    # Only github - write just github rules
                    filename = header_to_filename(parsed_header)
                    section_content = replace_header_with_proper_casing(
                        content, parsed_header
                    )
                    agent_instances["github"].write_rule(
                        section_content,
                        filename,
                        agent_dirs["github"]["rules"],
                        glob_pattern=None,
                    )

    # Process commands for all agents
    command_sections = {}
    if commands_text:
        _, command_sections = parse_sections(commands_text)
        agents = [agent_instances[name] for name in agents_to_process]
        command_dirs = {
            name: agent_dirs[name]["commands"] for name in agents_to_process
        }

        for section_name, section_content in command_sections.items():
            process_command_section(section_name, section_content, agents, command_dirs)

    # Generate root documentation (CLAUDE.md, GEMINI.md, etc.)
    for agent_name, agent_inst in agent_instances.items():
        agent_inst.generate_root_doc(
            general,
            rules_sections,
            command_sections,
            cwd,
            section_globs,
        )

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

    if len(created_dirs) == 1:
        success_msg = f"Created files in {created_dirs[0]} directory"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
    else:
        success_msg = f"Created files in {', '.join(created_dirs)} directories"
        typer.echo(typer.style(success_msg, fg=typer.colors.GREEN))
