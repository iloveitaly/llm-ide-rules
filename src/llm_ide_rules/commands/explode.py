"""Explode command: Convert instruction file to separate rule files."""

import logging
from pathlib import Path
from typing_extensions import Annotated

import structlog
import typer

from llm_ide_rules.agents import get_all_agents, get_agent
from llm_ide_rules.agents.base import (
    trim_content,
    replace_header_with_proper_casing,
    write_rule_file,
)
from llm_ide_rules.constants import load_section_globs, header_to_filename

logger = structlog.get_logger()


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
):
    """Convert instruction file to separate rule files."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )

    section_globs = load_section_globs(config)

    logger.info("Starting explode operation", input_file=input_file, config=config)

    cwd = Path.cwd()

    cursor_agent = get_agent("cursor")
    github_agent = get_agent("github")
    claude_agent = get_agent("claude")
    gemini_agent = get_agent("gemini")

    rules_dir = cwd / cursor_agent.rules_dir
    cursor_commands_dir = cwd / cursor_agent.commands_dir
    copilot_dir = cwd / github_agent.rules_dir
    github_prompts_dir = cwd / github_agent.commands_dir
    claude_commands_dir = cwd / claude_agent.commands_dir
    gemini_commands_dir = cwd / gemini_agent.commands_dir

    rules_dir.mkdir(parents=True, exist_ok=True)
    cursor_commands_dir.mkdir(parents=True, exist_ok=True)
    copilot_dir.mkdir(parents=True, exist_ok=True)
    github_prompts_dir.mkdir(parents=True, exist_ok=True)
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    gemini_commands_dir.mkdir(parents=True, exist_ok=True)

    input_path = cwd / input_file

    try:
        lines = input_path.read_text().splitlines(keepends=True)
    except FileNotFoundError:
        logger.error("Input file not found", input_file=str(input_path))
        raise typer.Exit(1)

    commands_path = input_path.parent / "commands.md"
    commands_lines = []
    if commands_path.exists():
        commands_lines = commands_path.read_text().splitlines(keepends=True)
        logger.info("Found commands file", commands_file=str(commands_path))

    general = extract_general(lines)
    if any(line.strip() for line in general):
        general_header = """
---
description:
alwaysApply: true
---
"""
        write_rule_file(rules_dir / "general.mdc", general_header, general)
        github_agent.write_general_instructions(general, cwd)

    found_sections = set()
    for section_name, glob_pattern in section_globs.items():
        section_content = extract_section(lines, f"## {section_name}")
        if any(line.strip() for line in section_content):
            found_sections.add(section_name)
            filename = header_to_filename(section_name)

            section_content = replace_header_with_proper_casing(
                section_content, section_name
            )

            cursor_agent.write_rule(
                section_content, filename, rules_dir, glob_pattern
            )
            github_agent.write_rule(
                section_content, filename, copilot_dir, glob_pattern
            )

    for section_name in section_globs:
        if section_name not in found_sections:
            logger.warning("Section not found in file", section=section_name)

    for line in lines:
        if line.startswith("## "):
            section_name = line.strip()[3:]
            if not any(
                section_name.lower() == mapped_section.lower()
                for mapped_section in section_globs
            ):
                logger.warning(
                    "Unmapped section in instructions.md, treating as always-apply rule",
                    section=section_name,
                )
                section_content = extract_section(lines, f"## {section_name}")
                process_unmapped_as_always_apply(
                    section_name,
                    section_content,
                    cursor_agent,
                    github_agent,
                    rules_dir,
                    copilot_dir,
                )

    if commands_lines:
        command_sections = extract_all_sections(commands_lines)
        agents = [cursor_agent, github_agent, claude_agent, gemini_agent]
        command_dirs = {
            "cursor": cursor_commands_dir,
            "github": github_prompts_dir,
            "claude": claude_commands_dir,
            "gemini": gemini_commands_dir,
        }
        for section_name, section_content in command_sections.items():
            process_command_section(section_name, section_content, agents, command_dirs)

    logger.info(
        "Explode operation completed",
        cursor_rules=str(rules_dir),
        cursor_commands=str(cursor_commands_dir),
        copilot_instructions=str(copilot_dir),
        github_prompts=str(github_prompts_dir),
        claude_commands=str(claude_commands_dir),
        gemini_commands=str(gemini_commands_dir),
    )
    typer.echo(
        "Created rules and commands in .cursor/, .claude/, .github/, and .gemini/ directories"
    )
