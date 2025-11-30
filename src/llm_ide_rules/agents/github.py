"""GitHub/Copilot agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files_github,
    resolve_header_from_stem,
    strip_yaml_frontmatter,
    strip_header,
    trim_content,
    write_rule_file,
    extract_description_and_filter_content,
)
from llm_ide_rules.constants import header_to_filename


class GitHubAgent(BaseAgent):
    """Agent for GitHub Copilot."""

    name = "github"
    rules_dir = ".github/instructions"
    commands_dir = ".github/prompts"
    rule_extension = ".instructions.md"
    command_extension = ".prompt.md"

    def bundle_rules(self, output_file: Path, section_globs: dict) -> bool:
        """Bundle GitHub instruction files into a single output file."""
        base_dir = output_file.parent
        instructions_path = base_dir / self.rules_dir
        copilot_general = base_dir / ".github" / "copilot-instructions.md"
        instr_files = list(instructions_path.glob(f"*{self.rule_extension}"))

        ordered_instructions = get_ordered_files_github(
            instr_files, list(section_globs.keys())
        )

        content_written = False
        with open(output_file, "w") as out:
            if copilot_general.exists():
                content = copilot_general.read_text().strip()
                if content:
                    out.write(content)
                    out.write("\n\n")
                    content_written = True

            for instr_file in ordered_instructions:
                content = instr_file.read_text().strip()
                if not content:
                    continue

                content = strip_yaml_frontmatter(content)
                content = strip_header(content)
                base_stem = instr_file.stem.replace(".instructions", "")
                header = resolve_header_from_stem(base_stem, section_globs)
                out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")
                content_written = True

        return content_written

    def bundle_commands(self, output_file: Path, section_globs: dict) -> bool:
        """Bundle GitHub prompt files into a single output file."""
        prompts_path = output_file.parent / self.commands_dir
        if not prompts_path.exists():
            return False

        prompt_files = list(prompts_path.glob(f"*{self.command_extension}"))
        if not prompt_files:
            return False

        prompt_dict = {}
        for f in prompt_files:
            base_stem = f.stem.replace(".prompt", "")
            prompt_dict[base_stem] = f

        ordered_prompts = []
        for section_name in section_globs.keys():
            filename = header_to_filename(section_name)
            if filename in prompt_dict:
                ordered_prompts.append(prompt_dict[filename])
                del prompt_dict[filename]

        remaining_prompts = sorted(prompt_dict.values(), key=lambda p: p.name)
        ordered_prompts.extend(remaining_prompts)

        content_written = False
        with open(output_file, "w") as out:
            for prompt_file in ordered_prompts:
                content = prompt_file.read_text().strip()
                if not content:
                    continue

                content = strip_yaml_frontmatter(content)
                content = strip_header(content)
                base_stem = prompt_file.stem.replace(".prompt", "")
                header = resolve_header_from_stem(base_stem, section_globs)
                out.write(f"## {header}\n\n")
                out.write(content)
                out.write("\n\n")
                content_written = True

        return content_written

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
    ) -> None:
        """Write a GitHub instruction file (.instructions.md) with YAML frontmatter."""
        filepath = rules_dir / f"{filename}{self.rule_extension}"

        if glob_pattern:
            header_yaml = f"""---
applyTo: "{glob_pattern}"
---
"""
        else:
            header_yaml = ""

        write_rule_file(filepath, header_yaml, content_lines)

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write a GitHub prompt file (.prompt.md) with YAML frontmatter."""
        filepath = commands_dir / f"{filename}{self.command_extension}"

        description, filtered_content = extract_description_and_filter_content(
            content_lines, ""
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

    def write_general_instructions(self, content_lines: list[str], base_dir: Path) -> None:
        """Write the general copilot-instructions.md file (no frontmatter)."""
        filepath = base_dir / ".github" / "copilot-instructions.md"
        write_rule_file(filepath, "", content_lines)

