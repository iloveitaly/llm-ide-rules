#!/usr/bin/env python3
"""
Convert copilot-instructions sections into Cursor rule files.
Usage: python3 explode.py [input_markdown]
"""
import os
import sys
import argparse

# Mapping of section headers to their file globs
SECTION_GLOBS = {
    "Python": "**/*.py",
    "React": "**/*.tsx", 
    "Shell": "**/*.sh",
    "TypeScript": "**/*.ts,**/*.tsx",
    "FastAPI": "app/routes/**/*.py",
    "React Router": "web/app/routes/**/*.tsx",
}

def generate_cursor_frontmatter(glob):
    """Generate Cursor rule frontmatter for a given glob pattern."""
    return f"""---
description:
globs: {glob}
alwaysApply: false
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
    """
    content = []
    in_section = False
    for line in lines:
        if in_section:
            if line.startswith("## "):
                break
            content.append(line)
        elif line.strip() == header:
            in_section = True
    return content


def write_rule(path, header_yaml, content_lines):
    """
    Write a rule file with front matter and content.
    """
    with open(path, "w") as f:
        f.write(header_yaml.strip() + "\n")
        for line in content_lines:
            f.write(line)


def header_to_filename(header):
    return header.lower().replace(' ', '-')


def main():
    parser = argparse.ArgumentParser(
        description="Convert copilot-instructions to Cursor rules"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="instructions.md",
        help="Input markdown file"
    )
    args = parser.parse_args()

    rules_dir = os.path.join(".cursor", "rules")
    copilot_dir = os.path.join(".github", "instructions")
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(copilot_dir, exist_ok=True)

    try:
        with open(args.input, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.")
        sys.exit(1)

    # General instructions
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
        write_rule(os.path.join(".github", "copilot-instructions.md"), "", general)

    # Process each section dynamically
    for section_name, glob in SECTION_GLOBS.items():
        section_content = extract_section(lines, f"## {section_name}")
        if any(line.strip() for line in section_content):
            filename = header_to_filename(section_name)
            
            # Write cursor rule
            cursor_header = generate_cursor_frontmatter(glob)
            write_rule(os.path.join(rules_dir, filename + ".mdc"), cursor_header, section_content)
            
            # Write copilot instruction
            copilot_header = generate_copilot_frontmatter(glob)
            write_rule(os.path.join(copilot_dir, filename + ".instructions.md"), copilot_header, section_content)

    # Check for unmapped sections
    for line in lines:
        if line.startswith("## "):
            section_header = line.strip()
            section_name = section_header[3:]  # Remove "## "
            if section_name not in SECTION_GLOBS:
                print(f"Warning: Found unmapped section '{section_name}' - add to SECTION_GLOBS to process it")

    print("Created Cursor rules in .cursor/rules/ and Copilot instructions in .github/instructions/")


if __name__ == "__main__":
    main()
