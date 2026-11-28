"cursor IDE agent implementation"

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    write_rule_file,
)


class CursorAgent(BaseAgent):
    "agent for Cursor IDE"

    name = "cursor"
    rules_dir = ".cursor/rules"
    rule_extension = ".mdc"

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        "bundle Cursor rule files (.mdc) into a single output file"
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        rules_path = output_file.parent / rules_dir

        rule_ext = self.rule_extension
        if not rule_ext:
            return False

        rule_files = list(rules_path.glob(f"*{rule_ext}"))

        general = [f for f in rule_files if f.stem == "general"]
        others = [f for f in rule_files if f.stem != "general"]

        ordered_others = get_ordered_files(
            others, list(section_globs.keys()) if section_globs else None
        )
        ordered = general + ordered_others

        content_parts: list[str] = []
        for rule_file in ordered:
            file_content = rule_file.read_text().strip()
            if not file_content:
                continue

            lines = file_content.splitlines()
            extracted_header = None
            glob_pattern = None

            for line in lines:
                if line.startswith("## "):
                    extracted_header = line[3:].strip()
                    break

            glob_pattern = self._extract_glob_from_frontmatter(file_content)

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            if extracted_header:
                header = extracted_header
            else:
                header = resolve_header_from_stem(
                    rule_file.stem, section_globs if section_globs else {}
                )

            if rule_file.stem != "general":
                content_parts.append(f"## {header}\n\n")
                if glob_pattern:
                    content_parts.append(f"globs: {glob_pattern}\n\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        self._write_bundled_content(output_file, "".join(content_parts))
        return True

    def _extract_glob_from_frontmatter(self, content: str) -> str | None:
        "extract glob pattern from YAML frontmatter"

        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                break
            if lines[i].startswith("globs:"):
                glob_value = lines[i][6:].strip()
                return glob_value if glob_value else None

        return None

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        "write a Cursor rule file (.mdc) with YAML frontmatter"

        extension = self.rule_extension or ".mdc"
        filepath = rules_dir / f"{filename}{extension}"

        desc = description or filename.replace("-", " ").title()

        if glob_pattern and glob_pattern != "manual":
            header_yaml = f"""---
description: {desc}
globs: {glob_pattern}
alwaysApply: false
---
"""
        elif glob_pattern == "manual":
            header_yaml = f"""---
description: {desc}
globs: 
alwaysApply: false
---
"""
        else:
            header_yaml = f"""---
description: {desc}
globs: 
alwaysApply: true
---
"""
        write_rule_file(filepath, header_yaml, content_lines)

    def configure_agents_md(self, base_dir: Path) -> bool:
        "cursor doesn't require explicit configuration for AGENTS.md"

        return False

    def detect(self, base_dir: Path) -> bool:
        "detect if Cursor is in use in the given directory"

        return (base_dir / ".cursor").exists() or (base_dir / ".cursorrules").exists()
