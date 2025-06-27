#!/usr/bin/env python3
"""
Convert copilot-instructions sections into Cursor rule files.
Usage: python3 explode.py [input_markdown]
"""
import os
import sys
import argparse

# Mapping of section headers to their file globs or None for prompts
SECTION_GLOBS = {
    "Python": "**/*.py",
    "Python App": "**/*.py",
    "Pytest Integration Tests": "tests/integration/**/*.py",
    "FastAPI": "app/routes/**/*.py",

    "React": "**/*.tsx", 
    "React Router": "web/app/routes/**/*.tsx",
    "React Router Client Loader": None,

    "Shell": "**/*.sh",
    "TypeScript": "**/*.ts,**/*.tsx",
    "TypeScript DocString": None,

    # prompts (None indicates it's a prompt, not an instruction)
    "Secrets": None,
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
    trimmed_content = trim_content(content_lines)
    with open(path, "w") as f:
        f.write(header_yaml.strip() + "\n")
        for line in trimmed_content:
            f.write(line)


def header_to_filename(header):
    return header.lower().replace(' ', '-')


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


def extract_description_and_filter_content(content_lines, default_description):
    """Extract description from first non-empty line and return filtered content."""
    trimmed_content = trim_content(content_lines)
    description = ""
    description_line = None
    
    # Find the first non-empty, non-header line as description
    for i, line in enumerate(trimmed_content):
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):
            description = stripped_line
            description_line = i
            break
    
    # If no description found, use default
    if not description or description_line is None:
        description = default_description
        filtered_content = trimmed_content
    else:
        # Remove the description line from content
        filtered_content = trimmed_content[:description_line] + trimmed_content[description_line + 1:]
        # Trim again after removing description line
        filtered_content = trim_content(filtered_content)
    
    return description, filtered_content


def write_cursor_prompt(content_lines, filename, prompts_dir):
    """Write a Cursor prompt file with frontmatter including description."""
    filepath = os.path.join(prompts_dir, filename + ".mdc")
    
    default_description = f"Prompt for {filename.replace('-', ' ')}"
    description, filtered_content = extract_description_and_filter_content(content_lines, default_description)
    
    frontmatter = f"""---
description: {description}
---
"""
    
    with open(filepath, "w") as f:
        f.write(frontmatter)
        for line in filtered_content:
            f.write(line)


def write_github_prompt(content_lines, filename, prompts_dir):
    """Write a GitHub prompt file with proper frontmatter."""
    filepath = os.path.join(prompts_dir, filename + ".prompt.md")
    
    default_description = f"Generate a new {filename.replace('-', ' ')}"
    description, filtered_content = extract_description_and_filter_content(content_lines, default_description)
    
    frontmatter = f"""---
mode: 'agent'
description: '{description}'
---
"""
    
    with open(filepath, "w") as f:
        f.write(frontmatter)
        for line in filtered_content:
            f.write(line)


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
    github_prompts_dir = os.path.join(".github", "prompts")
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(copilot_dir, exist_ok=True)
    os.makedirs(github_prompts_dir, exist_ok=True)

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
    found_sections = set()
    for section_name, glob_or_description in SECTION_GLOBS.items():
        section_content = extract_section(lines, f"## {section_name}")
        if any(line.strip() for line in section_content):
            found_sections.add(section_name)
            filename = header_to_filename(section_name)
            
            if glob_or_description is not None:
                # It's a glob pattern - create instruction files
                cursor_header = generate_cursor_frontmatter(glob_or_description)
                write_rule(os.path.join(rules_dir, filename + ".mdc"), cursor_header, section_content)
                
                copilot_header = generate_copilot_frontmatter(glob_or_description)
                write_rule(os.path.join(copilot_dir, filename + ".instructions.md"), copilot_header, section_content)
            else:
                # It's a prompt - create prompt files
                write_cursor_prompt(section_content, filename, rules_dir)
                write_github_prompt(section_content, filename, github_prompts_dir)

    # Check for sections in mapping that don't exist in the file
    for section_name in SECTION_GLOBS:
        if section_name not in found_sections:
            print(f"Warning: Section '{section_name}' specified in SECTION_GLOBS but not found in instructions file")

    # Check for unmapped sections
    for line in lines:
        if line.startswith("## "):
            section_header = line.strip()
            section_name = section_header[3:]  # Remove "## "
            if section_name not in SECTION_GLOBS:
                print(f"Warning: Found unmapped section '{section_name}' - add to SECTION_GLOBS to process it")

    print("Created Cursor rules in .cursor/rules/, Copilot instructions in .github/instructions/, and prompts in respective directories")


if __name__ == "__main__":
    main()
