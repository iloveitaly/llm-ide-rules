"github/Copilot agent implementation"

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files_github,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    write_rule_file,
)


class GitHubAgent(BaseAgent):
    "agent for GitHub Copilot"

    name = "github"
    rules_dir = ".github/instructions"
    rule_extension = ".instructions.md"

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        "bundle GitHub instruction files into a single output file"
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        base_dir = output_file.parent
        instructions_path = base_dir / rules_dir
        copilot_general = base_dir / ".github" / "copilot-instructions.md"

        rule_ext = self.rule_extension
        if not rule_ext:
            return False

        instr_files = list(instructions_path.glob(f"*{rule_ext}"))

        ordered_instructions = get_ordered_files_github(
            instr_files, list(section_globs.keys()) if section_globs else None
        )

        content_parts: list[str] = []
        if copilot_general.exists():
            content = copilot_general.read_text().strip()
            if content:
                content_parts.append(content)
                content_parts.append("\n\n")

        for instr_file in ordered_instructions:
            file_content = instr_file.read_text().strip()
            if not file_content:
                continue

            apply_to_pattern = self._extract_apply_to_from_frontmatter(file_content)

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)
            base_stem = instr_file.stem.replace(".instructions", "")
            header = resolve_header_from_stem(
                base_stem, section_globs if section_globs else {}
            )
            content_parts.append(f"## {header}\n\n")
            if apply_to_pattern:
                content_parts.append(f"globs: {apply_to_pattern}\n\n")
            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        self._write_bundled_content(output_file, "".join(content_parts))
        return True

    def _extract_apply_to_from_frontmatter(self, content: str) -> str | None:
        "extract applyTo pattern from YAML frontmatter"

        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                break
            if lines[i].startswith("applyTo:"):
                apply_to_value = lines[i][8:].strip().strip('"').strip("'")
                return apply_to_value if apply_to_value else None

        return None

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        "write a GitHub instruction file (.instructions.md) with YAML frontmatter"

        extension = self.rule_extension or ".instructions.md"
        filepath = rules_dir / f"{filename}{extension}"

        if glob_pattern and glob_pattern != "manual":
            header_yaml = f"""---
applyTo: "{glob_pattern}"
---
"""
        else:
            header_yaml = ""

        write_rule_file(filepath, header_yaml, content_lines)

    def write_general_instructions(
        self, content_lines: list[str], base_dir: Path
    ) -> None:
        "write the general copilot-instructions.md file (no frontmatter)"

        filepath = base_dir / ".github" / "copilot-instructions.md"
        write_rule_file(filepath, "", content_lines)

    def configure_agents_md(self, base_dir: Path) -> bool:
        "configure VS Code to use AGENTS.md"

        from llm_ide_rules.utils import modify_json_file

        settings_path = base_dir / ".vscode" / "settings.json"

        updates = {"chat.useAgentsMdFile": True, "chat.useNestedAgentsMdFiles": True}

        return modify_json_file(settings_path, updates)

    def detect(self, base_dir: Path) -> bool:
        "detect if GitHub Copilot is in use in the given directory"

        github_dir = base_dir / ".github"
        return (github_dir / "copilot-instructions.md").exists() or (
            github_dir / "instructions"
        ).exists()
