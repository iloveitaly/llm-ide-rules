"""Explode command: Convert instruction file to separate rule files."""

import os
import sys
from pathlib import Path
from typing_extensions import Annotated

import typer
import structlog
import logging

from llm_ide_rules.constants import load_section_globs, header_to_filename

logger = structlog.get_logger()


def generate_cursor_frontmatter(glob):
    """Generate Cursor rule frontmatter for a given glob pattern."""
    return f"""---
description:
globs: {glob}
alwaysApply: false
---
"""


def generate_cursor_always_apply_frontmatter():
    """Generate Cursor rule frontmatter for always-apply rules."""
    return """---
description:
alwaysApply: true
---
"""


def generate_copilot_frontmatter(glob):
    """Generate Copilot instruction frontmatter for a given glob pattern."""
    return f"""---
applyTo: "{glob}"
---
"""


def extract_general(lines):
    """
    Extract lines before the first section header '## '.
    """
    general = []
    for line in lines:
        if line.startswith("## "):
            break
        general.append(line)
    return general


def extract_section(lines, header):
    """
    Extract lines under a given section header until the next header or EOF.
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
            content.append(line)  # Include the header itself
    return content


def extract_all_sections(lines):
    """Extract all sections from lines, returning dict of section_name -> content_lines."""
    sections = {}
    current_section = None
    current_content = []

    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections[current_section] = current_content

            current_section = line.strip()[3:]  # Remove "## "
            current_content = [line]
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = current_content

    return sections


def write_rule(path, header_yaml, content_lines):
    """
    Write a rule file with front matter and content.
    """
    trimmed_content = trim_content(content_lines)
    with open(path, "w") as f:
        f.write(header_yaml.strip() + "\n")
        for line in trimmed_content:
            f.write(line)


def trim_content(content_lines):
    """Remove leading and trailing empty lines from content."""
    # Find first non-empty line
    start = 0
    for i, line in enumerate(content_lines):
        if line.strip():
            start = i
            break
    else:
        # All lines are empty
        return []

    # Find last non-empty line
    end = len(content_lines)
    for i in range(len(content_lines) - 1, -1, -1):
        if content_lines[i].strip():
            end = i + 1
            break

    return content_lines[start:end]


def replace_header_with_proper_casing(content_lines, proper_header):
    """Replace the first header in content with the properly cased version."""
    if not content_lines:
        return content_lines

    # Find and replace the first header line
    for i, line in enumerate(content_lines):
        if line.startswith("## "):
            content_lines[i] = f"## {proper_header}\n"
            break

    return content_lines


def extract_description_and_filter_content(content_lines, default_description):
    """Extract description from first non-empty line that starts with 'Description:' and return filtered content."""
    trimmed_content = trim_content(content_lines)
    description = ""
    description_line = None

    # Find the first non-empty, non-header line that starts with "Description:"
    for i, line in enumerate(trimmed_content):
        stripped_line = line.strip()
        if (
            stripped_line
            and not stripped_line.startswith("#")
            and not stripped_line.startswith("##")
        ):
            if stripped_line.startswith("Description:"):
                # Extract the description text after "Description:"
                description = stripped_line[len("Description:") :].strip()
                description_line = i
                break
            else:
                # Found a non-header line that doesn't start with Description:, stop looking
                break

    # Only use explicit descriptions - no fallback extraction
    if description and description_line is not None:
        # Remove the description line from content
        filtered_content = (
            trimmed_content[:description_line] + trimmed_content[description_line + 1 :]
        )
        # Trim again after removing description line
        filtered_content = trim_content(filtered_content)
    else:
        # No description found, keep all content
        filtered_content = trimmed_content

    return description, filtered_content


def write_cursor_prompt(content_lines, filename, prompts_dir, section_name=None):
    """Write a Cursor prompt file with frontmatter including description."""
    filepath = os.path.join(prompts_dir, filename + ".mdc")

    # Don't generate a default description, leave empty if none found
    default_description = ""
    description, filtered_content = extract_description_and_filter_content(
        content_lines, default_description
    )

    with open(filepath, "w") as f:
        # Only add frontmatter if description is not empty
        if description:
            frontmatter = f"""---
description: {description}
---
"""
            f.write(frontmatter)

        for line in filtered_content:
            f.write(line)


def write_github_prompt(content_lines, filename, prompts_dir, section_name=None):
    """Write a GitHub prompt file with proper frontmatter."""
    filepath = os.path.join(prompts_dir, filename + ".prompt.md")

    # Don't generate a default description, leave empty if none found
    default_description = ""
    description, filtered_content = extract_description_and_filter_content(
        content_lines, default_description
    )

    frontmatter = f"""---
mode: 'agent'
description: '{description}'
---
"""

    with open(filepath, "w") as f:
        f.write(frontmatter)
        for line in filtered_content:
            f.write(line)


def write_cursor_command(content_lines, filename, commands_dir, section_name=None):
    """Write a Cursor command file (plain markdown, no frontmatter)."""
    filepath = os.path.join(commands_dir, filename + ".md")

    trimmed = trim_content(content_lines)

    # Strip the header from content (first line starting with ##)
    filtered_content = []
    found_header = False
    for line in trimmed:
        if not found_header and line.startswith("## "):
            found_header = True
            continue
        filtered_content.append(line)

    # Trim again after removing header
    filtered_content = trim_content(filtered_content)

    with open(filepath, "w") as f:
        for line in filtered_content:
            f.write(line)


def write_claude_command(content_lines, filename, commands_dir, section_name=None):
    """Write a Claude Code command file (plain markdown, no frontmatter)."""
    filepath = os.path.join(commands_dir, filename + ".md")

    trimmed = trim_content(content_lines)

    # Strip the header from content (first line starting with ##)
    filtered_content = []
    found_header = False
    for line in trimmed:
        if not found_header and line.startswith("## "):
            found_header = True
            continue
        filtered_content.append(line)

    # Trim again after removing header
    filtered_content = trim_content(filtered_content)

    with open(filepath, "w") as f:
        for line in filtered_content:
            f.write(line)


def write_gemini_command(content_lines, filename, commands_dir, section_name=None):
    """Write a Gemini CLI command file (TOML format)."""
    filepath = os.path.join(commands_dir, filename + ".toml")

    description, filtered_content = extract_description_and_filter_content(
        content_lines, ""
    )

    # Strip the header from content (first line starting with ##)
    final_content = []
    found_header = False
    for line in filtered_content:
        if not found_header and line.startswith("## "):
            found_header = True
            continue
        final_content.append(line)

    # Trim and convert to string
    final_content = trim_content(final_content)
    content_str = "".join(final_content).strip()

    with open(filepath, "w") as f:
        f.write(f'name = "{filename}"\n')
        if description:
            f.write(f'description = "{description}"\n')
        else:
            f.write(f'description = "{section_name or filename}"\n')
        f.write('\n[command]\n')
        f.write('shell = """\n')
        f.write(content_str)
        f.write('\n"""\n')


def process_command_section(section_name, section_content, cursor_commands_dir, github_prompts_dir, claude_commands_dir, gemini_commands_dir):
    """Process a section as a command."""
    if not any(line.strip() for line in section_content):
        return False

    filename = header_to_filename(section_name)
    section_content = replace_header_with_proper_casing(section_content, section_name)

    write_cursor_command(section_content, filename, cursor_commands_dir, section_name)
    write_github_prompt(section_content, filename, github_prompts_dir, section_name)
    write_claude_command(section_content, filename, claude_commands_dir, section_name)
    write_gemini_command(section_content, filename, gemini_commands_dir, section_name)
    return True


def process_unmapped_as_always_apply(section_name, section_content, rules_dir, copilot_dir):
    """Process an unmapped section as an always-apply rule."""
    if not any(line.strip() for line in section_content):
        return False

    filename = header_to_filename(section_name)
    section_content = replace_header_with_proper_casing(section_content, section_name)

    # Create always-apply rule files
    cursor_header = generate_cursor_always_apply_frontmatter()
    write_rule(
        os.path.join(rules_dir, filename + ".mdc"),
        cursor_header,
        section_content,
    )

    # Copilot doesn't have alwaysApply, so we skip the glob
    write_rule(
        os.path.join(copilot_dir, filename + ".instructions.md"),
        "",
        section_content,
    )

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

    # Load section globs (with optional custom config)
    SECTION_GLOBS = load_section_globs(config)

    logger.info("Starting explode operation", input_file=input_file, config=config)

    # Work in current directory ($PWD)
    rules_dir = os.path.join(os.getcwd(), ".cursor", "rules")
    cursor_commands_dir = os.path.join(os.getcwd(), ".cursor", "commands")
    copilot_dir = os.path.join(os.getcwd(), ".github", "instructions")
    github_prompts_dir = os.path.join(os.getcwd(), ".github", "prompts")
    claude_commands_dir = os.path.join(os.getcwd(), ".claude", "commands")
    gemini_commands_dir = os.path.join(os.getcwd(), ".gemini", "commands")

    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(cursor_commands_dir, exist_ok=True)
    os.makedirs(copilot_dir, exist_ok=True)
    os.makedirs(github_prompts_dir, exist_ok=True)
    os.makedirs(claude_commands_dir, exist_ok=True)
    os.makedirs(gemini_commands_dir, exist_ok=True)

    input_path = Path(os.getcwd()) / input_file

    try:
        lines = input_path.read_text().splitlines(keepends=True)
    except FileNotFoundError:
        logger.error("Input file not found", input_file=str(input_path))
        raise typer.Exit(1)

    # Check for optional commands.md in same directory
    commands_path = input_path.parent / "commands.md"
    commands_lines = []
    if commands_path.exists():
        commands_lines = commands_path.read_text().splitlines(keepends=True)
        logger.info("Found commands file", commands_file=str(commands_path))

    # General instructions (content before first ## header)
    general = extract_general(lines)
    if any(line.strip() for line in general):
        general_header = """
---
description:
alwaysApply: true
---
"""
        write_rule(os.path.join(rules_dir, "general.mdc"), general_header, general)
        # Copilot general instructions (no frontmatter)
        write_rule(
            os.path.join(os.getcwd(), ".github", "copilot-instructions.md"), "", general
        )

    # Process mapped sections from instructions.md
    found_sections = set()
    for section_name, glob_pattern in SECTION_GLOBS.items():
        section_content = extract_section(lines, f"## {section_name}")
        if any(line.strip() for line in section_content):
            found_sections.add(section_name)
            filename = header_to_filename(section_name)

            section_content = replace_header_with_proper_casing(
                section_content, section_name
            )

            # Create rule files with glob pattern
            cursor_header = generate_cursor_frontmatter(glob_pattern)
            write_rule(
                os.path.join(rules_dir, filename + ".mdc"),
                cursor_header,
                section_content,
            )

            copilot_header = generate_copilot_frontmatter(glob_pattern)
            write_rule(
                os.path.join(copilot_dir, filename + ".instructions.md"),
                copilot_header,
                section_content,
            )

    # Check for sections in mapping that don't exist in the file
    for section_name in SECTION_GLOBS:
        if section_name not in found_sections:
            logger.warning("Section not found in file", section=section_name)

    # Process unmapped sections in instructions.md as always-apply rules
    for line in lines:
        if line.startswith("## "):
            section_name = line.strip()[3:]  # Remove "## "
            if not any(
                section_name.lower() == mapped_section.lower()
                for mapped_section in SECTION_GLOBS
            ):
                logger.warning(
                    "Unmapped section in instructions.md, treating as always-apply rule",
                    section=section_name
                )
                section_content = extract_section(lines, f"## {section_name}")
                process_unmapped_as_always_apply(
                    section_name, section_content, rules_dir, copilot_dir
                )

    # Process commands from commands.md if it exists
    if commands_lines:
        command_sections = extract_all_sections(commands_lines)
        for section_name, section_content in command_sections.items():
            process_command_section(
                section_name,
                section_content,
                cursor_commands_dir,
                github_prompts_dir,
                claude_commands_dir,
                gemini_commands_dir,
            )

    logger.info(
        "Explode operation completed",
        cursor_rules=rules_dir,
        cursor_commands=cursor_commands_dir,
        copilot_instructions=copilot_dir,
        github_prompts=github_prompts_dir,
        claude_commands=claude_commands_dir,
        gemini_commands=gemini_commands_dir,
    )
    typer.echo(
        "Created rules and commands in .cursor/, .claude/, .github/, and .gemini/ directories"
    )
