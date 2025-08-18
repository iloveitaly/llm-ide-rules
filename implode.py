#!/usr/bin/env python3
"""
DEPRECATED: Use `llm-rules implode` instead.

Bundle Cursor or Copilot instruction component files into a single instruction file.
Usage: python3 implode.py [cursor|github] [output_file]
"""

import os
import sys
import argparse
from pathlib import Path

print("WARNING: This script is deprecated. Please use 'llm-rules implode' instead.")
print("Install llm-rules with: uv tool install git+https://github.com/iloveitaly/llm-ide-prompts.git")
print("Usage: llm-rules implode cursor [output_file]")
print("       llm-rules implode github [output_file]")
print("")

# Add current directory to path for constants import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constants import SECTION_GLOBS, header_to_filename, filename_to_header


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
    copilot_general = Path(".github/copilot-instructions.md")
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


def main():
    parser = argparse.ArgumentParser(
        description="Bundle Cursor or Copilot rules into a single file."
    )
    parser.add_argument(
        "mode", choices=["cursor", "github"], help="Which rules to bundle"
    )
    parser.add_argument(
        "output", nargs="?", default="instructions.md", help="Output file"
    )
    args = parser.parse_args()

    if args.mode == "cursor":
        bundle_cursor_rules(".cursor/rules", args.output)
    else:
        bundle_github_instructions(".github/instructions", args.output)
    print(f"Bundled {args.mode} rules into {args.output}")


if __name__ == "__main__":
    main()
