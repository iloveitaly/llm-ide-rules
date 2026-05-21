"""Antigravity CLI agent implementation."""

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    get_ordered_files,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    trim_content,
    extract_description_and_filter_content,
)


class AntigravityAgent(BaseAgent):
    """Agent for Antigravity CLI."""

    name = "antigravity"
    rules_dir = ".agents/rules"
    commands_dir = ".agents/skills"
    rule_extension = ".md"
    command_extension = "/SKILL.md"

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        """Bundle Antigravity rule files (.md) into a single output file."""
        rules_dir = self.rules_dir
        if not rules_dir:
            return False

        rules_path = output_file.parent / rules_dir
        if not rules_path.exists():
            return False

        extension = self.rule_extension
        if not extension:
            return False

        rule_files = list(rules_path.glob(f"*{extension}"))
        if not rule_files:
            return False

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

            desc, glob_pattern, always_apply = self._extract_metadata_from_frontmatter(file_content)

            extracted_header = None
            for line in file_content.splitlines():
                if line.startswith("## "):
                    extracted_header = line[3:].strip()
                    break

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            # Collapse consecutive empty lines in content
            content_lines = content.splitlines()
            cleaned_lines = []
            for line in content_lines:
                if not line.strip():
                    if cleaned_lines and cleaned_lines[-1].strip():
                        cleaned_lines.append("")
                else:
                    cleaned_lines.append(line)
            content = "\n".join(cleaned_lines)

            if rule_file.stem != "general":
                header = extracted_header or resolve_header_from_stem(
                    rule_file.stem, section_globs if section_globs else {}
                )
                content_parts.append(f"## {header}\n\n")

                has_meta = False
                if glob_pattern:
                    content_parts.append(f"globs: {glob_pattern}\n")
                    has_meta = True
                elif not always_apply:
                    content_parts.append("globs: manual\n")
                    has_meta = True

                if desc:
                    content_parts.append(f"Description: {desc}\n")
                    has_meta = True

                if has_meta:
                    content_parts.append("\n")

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        self._write_bundled_content(output_file, "".join(content_parts))
        return True

    def _extract_metadata_from_frontmatter(self, content: str) -> tuple[str | None, str | None, bool]:
        """Extract description, glob pattern, and alwaysApply from YAML frontmatter.

        Returns:
            tuple: (description, glob_pattern, always_apply)
        """
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None, None, False

        description = None
        glob_pattern = None
        always_apply = False

        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == "---":
                break
            if line.startswith("description:"):
                description = line[len("description:"):].strip().strip('"').strip("'")
            elif line.startswith("alwaysApply:"):
                val = line[len("alwaysApply:"):].strip().lower()
                always_apply = (val == "true")
            elif line.startswith("globs:"):
                globs_val = line[len("globs:"):].strip()
                # Parse either inline list ["*.py"] or [] or list on next lines
                if globs_val.startswith("[") and globs_val.endswith("]"):
                    inner = globs_val[1:-1].strip()
                    if inner:
                        glob_pattern = inner.strip().strip('"').strip("'")
                else:
                    if not globs_val:
                        for j in range(i + 1, len(lines)):
                            next_line = lines[j].strip()
                            if next_line == "---" or ":" in next_line:
                                break
                            if next_line.startswith("-"):
                                glob_pattern = next_line[1:].strip().strip('"').strip("'")
                                break

        return description, glob_pattern, always_apply

    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        """Bundle Antigravity skill files (SKILL.md) into a single output file."""
        commands_dir = self.commands_dir
        if not commands_dir:
            return False

        commands_path = output_file.parent / commands_dir
        if not commands_path.exists():
            return False

        skill_files = list(commands_path.glob("**/SKILL.md"))
        if not skill_files:
            return False

        # Order by parent directory name (which is the skill/stem name)
        ordered_skills = get_ordered_files(
            skill_files, list(section_globs.keys()) if section_globs else None
        )

        content_parts: list[str] = []
        for skill_file in ordered_skills:
            file_content = skill_file.read_text().strip()
            if not file_content:
                continue

            name = None
            desc = None
            lines = file_content.splitlines()
            if lines and lines[0].strip() == "---":
                for i in range(1, len(lines)):
                    line = lines[i].strip()
                    if line == "---":
                        break
                    if line.startswith("name:"):
                        name = line[len("name:"):].strip().strip('"').strip("'")
                    elif line.startswith("description:"):
                        desc = line[len("description:"):].strip().strip('"').strip("'")

            content = strip_yaml_frontmatter(file_content)

            content_lines = content.splitlines()
            if content_lines and content_lines[0].startswith("# "):
                header_name = content_lines[0][2:].strip()
                content_lines[0] = f"## {header_name}"
            else:
                header_name = resolve_header_from_stem(
                    skill_file.parent.name, section_globs if section_globs else {}
                )
                content_parts.append(f"## {header_name}\n\n")

            content = "\n".join(content_lines)

            if desc and f"Description: {desc}" not in content:
                lines = content.splitlines()
                if lines and lines[0].startswith("## "):
                    lines.insert(1, f"Description: {desc}")
                    lines.insert(2, "")
                    content = "\n".join(lines)

            # Collapse consecutive empty lines in content
            content_lines = content.splitlines()
            cleaned_lines = []
            for line in content_lines:
                if not line.strip():
                    if cleaned_lines and cleaned_lines[-1].strip():
                        cleaned_lines.append("")
                else:
                    cleaned_lines.append(line)
            content = "\n".join(cleaned_lines)

            content_parts.append(content)
            content_parts.append("\n\n")

        if not content_parts:
            return False

        self._write_bundled_content(output_file, "".join(content_parts))
        return True

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        """Write an Antigravity rule file (.md) with YAML frontmatter."""
        extension = self.rule_extension or ".md"
        filepath = rules_dir / f"{filename}{extension}"

        desc, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )
        if not desc:
            desc = description or resolve_header_from_stem(filename, {})

        if glob_pattern is None or filename == "general":
            globs_str = "[]"
            always_apply = "true"
        elif glob_pattern == "manual":
            globs_str = "[]"
            always_apply = "false"
        else:
            globs_str = f'["{glob_pattern}"]'
            always_apply = "false"

        frontmatter = f"---\ndescription: {desc}\nglobs: {globs_str}\nalwaysApply: {always_apply}\n---\n\n"

        trimmed = trim_content(filtered_content)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(frontmatter + "".join(trimmed))

    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        """Write an Antigravity skill file (.agents/skills/<filename>/SKILL.md) with YAML frontmatter."""
        filepath = commands_dir / filename / "SKILL.md"

        desc, filtered_content = extract_description_and_filter_content(
            content_lines, ""
        )
        if not desc:
            desc = section_name or filename.replace("-", " ").title()

        # Find the header
        header = None
        for line in content_lines:
            if line.startswith("## "):
                header = line[3:].strip()
                break

        if not header:
            header = section_name or filename.replace("-", " ").title()

        # Replace first ## Header with # Header
        final_content = []
        found_header = False
        for line in filtered_content:
            if not found_header and line.startswith("## "):
                found_header = True
                final_content.append(f"# {header}\n")
                continue
            final_content.append(line)

        frontmatter = f"---\nname: {filename}\ndescription: {desc}\n---\n\n"

        trimmed = trim_content(final_content)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(frontmatter + "".join(trimmed))
