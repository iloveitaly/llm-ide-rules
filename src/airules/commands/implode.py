"""Implode command: Bundle rule files into a single instruction file."""

import os
from pathlib import Path
from typing_extensions import Annotated
import logging

import typer
import structlog

from airules.constants import SECTION_GLOBS, header_to_filename, filename_to_header

logger = structlog.get_logger()


def get_ordered_files(file_list, section_globs_keys):
    """Order files based on SECTION_GLOBS key order, with unmapped files at the end."""
    file_dict = {f.stem: f for f in file_list}
    ordered_files = []

    # Add files in SECTION_GLOBS order
    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    # Add any remaining files (not in SECTION_GLOBS) sorted alphabetically
    remaining_files = sorted(file_dict.values(), key=lambda p: p.name)
    ordered_files.extend(remaining_files)

    return ordered_files


def get_ordered_files_github(file_list, section_globs_keys):
    """Order GitHub instruction files based on SECTION_GLOBS key order, with unmapped files at the end.
    Handles .instructions suffix by stripping it for ordering purposes."""
    # Create dict mapping base filename (without .instructions) to the actual file
    file_dict = {}
    for f in file_list:
        base_stem = f.stem.replace(".instructions", "")
        file_dict[base_stem] = f

    ordered_files = []

    # Add files in SECTION_GLOBS order
    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    # Add any remaining files (not in SECTION_GLOBS) sorted alphabetically
    remaining_files = sorted(file_dict.values(), key=lambda p: p.name)
    ordered_files.extend(remaining_files)

    return ordered_files


def bundle_cursor_rules(rules_dir, output_file):
    """Bundle Cursor rule files into a single file."""
    rule_files = list(Path(rules_dir).glob("*.mdc"))
    general = [f for f in rule_files if f.stem == "general"]
    others = [f for f in rule_files if f.stem != "general"]

    # Order the non-general files based on SECTION_GLOBS
    ordered_others = get_ordered_files(others, SECTION_GLOBS.keys())
    ordered = general + ordered_others

    def resolve_header_from_stem(stem):
        """Return the canonical header for a given filename stem.

        Prefer exact header names from SECTION_GLOBS (preserves acronyms like FastAPI, TypeScript).
        Fallback to title-casing the filename when not found in SECTION_GLOBS.
        """
        for section_name in SECTION_GLOBS.keys():
            if header_to_filename(section_name) == stem:
                return section_name
        return filename_to_header(stem)

    with open(output_file, "w") as out:
        for rule_file in ordered:
            with open(rule_file, "r") as f:
                content = f.read().strip()
                if not content:
                    continue
                content = strip_yaml_frontmatter(content)
                content = strip_header(content)
                # Use canonical header names from SECTION_GLOBS when available
                header = resolve_header_from_stem(rule_file.stem)
                if rule_file.stem != "general":
                    out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")


def strip_yaml_frontmatter(text):
    """Strip YAML frontmatter from text."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        # Find the next '---' after the first
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :]).lstrip("\n")
    return text


def strip_header(text):
    """Remove the first markdown header (## Header) from text if present."""
    lines = text.splitlines()
    if lines and lines[0].startswith("## "):
        # Remove the header line and any immediately following empty lines
        remaining_lines = lines[1:]
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines = remaining_lines[1:]
        return "\n".join(remaining_lines)
    return text


def bundle_github_instructions(instructions_dir, output_file):
    """Bundle GitHub instruction files into a single file."""
    copilot_general = Path(os.getcwd()) / ".github" / "copilot-instructions.md"
    instr_files = list(Path(instructions_dir).glob("*.instructions.md"))

    # Order the instruction files based on SECTION_GLOBS
    # We need to create a modified version that strips .instructions from stems for ordering
    ordered_files = get_ordered_files_github(instr_files, SECTION_GLOBS.keys())

    def resolve_header_from_stem(stem):
        """Return the canonical header for a given filename stem.

        Prefer exact header names from SECTION_GLOBS (preserves acronyms like FastAPI, TypeScript).
        Fallback to title-casing the filename when not found in SECTION_GLOBS.
        """
        for section_name in SECTION_GLOBS.keys():
            if header_to_filename(section_name) == stem:
                return section_name
        return filename_to_header(stem)

    with open(output_file, "w") as out:
        # Write general copilot instructions if present
        if copilot_general.exists():
            content = copilot_general.read_text().strip()
            if content:
                out.write(content)
                out.write("\n\n")
        for instr_file in ordered_files:
            with open(instr_file, "r") as f:
                content = f.read().strip()
                if not content:
                    continue
                content = strip_yaml_frontmatter(content)
                content = strip_header(content)
                # Use canonical header names from SECTION_GLOBS when available
                base_stem = instr_file.stem.replace(".instructions", "")
                header = resolve_header_from_stem(base_stem)
                out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")


def cursor(
    output: Annotated[str, typer.Argument(help="Output file")] = "instructions.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
):
    """Bundle Cursor rules into a single file."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    
    rules_dir = os.path.join(os.getcwd(), ".cursor", "rules")
    output_path = os.path.join(os.getcwd(), output)
    
    logger.info("Bundling Cursor rules", rules_dir=rules_dir, output_file=output_path)
    
    if not Path(rules_dir).exists():
        logger.error("Cursor rules directory not found", rules_dir=rules_dir)
        raise typer.Exit(1)
    
    bundle_cursor_rules(rules_dir, output_path)
    logger.info("Cursor rules bundled successfully", output_file=output_path)
    print(f"Bundled cursor rules into {output}")


def github(
    output: Annotated[str, typer.Argument(help="Output file")] = "instructions.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
):
    """Bundle GitHub/Copilot instructions into a single file."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )
    
    instructions_dir = os.path.join(os.getcwd(), ".github", "instructions")
    output_path = os.path.join(os.getcwd(), output)
    
    logger.info("Bundling GitHub instructions", instructions_dir=instructions_dir, output_file=output_path)
    
    if not Path(instructions_dir).exists():
        logger.error("GitHub instructions directory not found", instructions_dir=instructions_dir)
        raise typer.Exit(1)
    
    bundle_github_instructions(instructions_dir, output_path)
    logger.info("GitHub instructions bundled successfully", output_file=output_path)
    print(f"Bundled github instructions into {output}")


# Set the default subcommand
def implode_main(
    ctx: typer.Context,
    mode: Annotated[str, typer.Argument(help="Which rules to bundle")] = None,
    output: Annotated[str, typer.Argument(help="Output file")] = "instructions.md",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose logging")] = False,
):
    """Bundle rule files into a single instruction file."""
    if ctx.invoked_subcommand is not None:
        return
    
    if mode is None:
        print("Usage: llm-rules implode [cursor|github] [output_file]")
        print("\nOr use subcommands:")
        print("  llm-rules implode cursor [output_file]")
        print("  llm-rules implode github [output_file]")
        raise typer.Exit(1)
    
    if mode == "cursor":
        ctx.invoke(cursor, output=output, verbose=verbose)
    elif mode == "github":
        ctx.invoke(github, output=output, verbose=verbose)
    else:
        print(f"Unknown mode: {mode}. Use 'cursor' or 'github'")
        raise typer.Exit(1)