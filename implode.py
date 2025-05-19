#!/usr/bin/env python3
"""
Bundle Cursor or Copilot instruction component files into a single instruction file.
Usage: python3 implode.py [cursor|github] [output_file]
"""
import os
import sys
import argparse
from pathlib import Path

def bundle_cursor_rules(rules_dir, output_file):
    rule_files = list(Path(rules_dir).glob("*.mdc"))
    general = [f for f in rule_files if f.stem == "general"]
    others = sorted([f for f in rule_files if f.stem != "general"], key=lambda p: p.name)
    ordered = general + others
    with open(output_file, "w") as out:
        for rule_file in ordered:
            with open(rule_file, "r") as f:
                content = f.read().strip()
                if not content:
                    continue
                content = strip_yaml_frontmatter(content)
                # Convert dash-separated names to title case with spaces
                header = rule_file.stem.replace('-', ' ').title()
                if rule_file.stem != "general":
                    out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")

def strip_yaml_frontmatter(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == '---':
        # Find the next '---' after the first
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return '\n'.join(lines[i+1:]).lstrip('\n')
    return text

def bundle_github_instructions(instructions_dir, output_file):
    copilot_general = Path(".github/copilot-instructions.md")
    instr_files = list(Path(instructions_dir).glob("*.instructions.md"))
    others = sorted(instr_files, key=lambda p: p.name)
    with open(output_file, "w") as out:
        # Write general copilot instructions if present
        if copilot_general.exists():
            content = copilot_general.read_text().strip()
            if content:
                out.write(content)
                out.write("\n\n")
        for instr_file in others:
            with open(instr_file, "r") as f:
                content = f.read().strip()
                if not content:
                    continue
                content = strip_yaml_frontmatter(content)
                header = instr_file.stem.replace('.instructions','').replace('-', ' ').title()
                out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")

def main():
    parser = argparse.ArgumentParser(description="Bundle Cursor or Copilot rules into a single file.")
    parser.add_argument("mode", choices=["cursor", "github"], help="Which rules to bundle")
    parser.add_argument("output", nargs="?", default="instructions.md", help="Output file")
    args = parser.parse_args()

    if args.mode == "cursor":
        bundle_cursor_rules(".cursor/rules", args.output)
    else:
        bundle_github_instructions(".github/instructions", args.output)
    print(f"Bundled {args.mode} rules into {args.output}")

if __name__ == "__main__":
    main()
