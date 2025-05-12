#!/usr/bin/env python3
"""
Convert copilot-instructions sections into Cursor rule files.
Usage: python3 explode.py [input_markdown]
"""
import os
import sys
import argparse


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

    # Python section
    python_sec = extract_section(lines, "## Python")
    if any(line.strip() for line in python_sec):
        python_header = """
---
description:
globs: *.py
alwaysApply: false
---
"""
        write_rule(os.path.join(rules_dir, "python.mdc"), python_header, python_sec)
        # Copilot Python instructions
        copilot_python_header = """
---
applyTo: "**/*.py"
---
"""
        write_rule(os.path.join(copilot_dir, "python.instructions.md"), copilot_python_header, python_sec)

    # React section
    react_sec = extract_section(lines, "## React")
    if any(line.strip() for line in react_sec):
        react_header = """
---
description:
globs: *.tsx
alwaysApply: false
---
"""
        write_rule(os.path.join(rules_dir, "react.mdc"), react_header, react_sec)
        # Copilot React instructions
        copilot_react_header = """
---
applyTo: "**/*.tsx"
---
"""
        write_rule(os.path.join(copilot_dir, "react.instructions.md"), copilot_react_header, react_sec)

    # Shell Scripts section
    shell_sec = extract_section(lines, "## Shell Scripts")
    if any(line.strip() for line in shell_sec):
        shell_header = """
---
description:
globs: *.sh
alwaysApply: false
---
"""
        write_rule(os.path.join(rules_dir, "shell.mdc"), shell_header, shell_sec)
        # Copilot Shell instructions
        copilot_shell_header = """
---
applyTo: "**/*.sh"
---
"""
        write_rule(os.path.join(copilot_dir, "shell.instructions.md"), copilot_shell_header, shell_sec)

    # TypeScript section
    typescript_sec = extract_section(lines, "## TypeScript")
    if any(line.strip() for line in typescript_sec):
        typescript_header = """
---
description:
globs: *.ts
alwaysApply: false
---
"""
        write_rule(os.path.join(rules_dir, "typescript.mdc"), typescript_header, typescript_sec)
        # Copilot TypeScript instructions
        copilot_typescript_header = """
---
applyTo: "**/*.ts"
---
"""
        write_rule(os.path.join(copilot_dir, "typescript.instructions.md"), copilot_typescript_header, typescript_sec)

    print("Created Cursor rules in .cursor/rules/ and Copilot instructions in .github/instructions/")


if __name__ == "__main__":
    main()
