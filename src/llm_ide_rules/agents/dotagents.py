"shared base agent implementation for .agents layout"

from pathlib import Path

from llm_ide_rules.agents.base import (
    BaseAgent,
    extract_description_and_filter_content,
    extract_frontmatter_description,
    get_ordered_files,
    resolve_header_from_stem,
    strip_header,
    strip_yaml_frontmatter,
    trim_content,
)


class DotAgentsBaseAgent(BaseAgent):
    "base agent for tools using the .agents specification"

    rules_dir = ".agents/rules"
    rule_extension = ".md"

    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        "bundle .agents rule files (.md) into a single output file"

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

            desc, glob_pattern, always_apply = self._extract_metadata_from_frontmatter(
                file_content
            )

            extracted_header = None
            for line in file_content.splitlines():
                if line.startswith("## "):
                    extracted_header = line[3:].strip()
                    break

            content = strip_yaml_frontmatter(file_content)
            content = strip_header(content)

            # collapse consecutive empty lines in content
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

                stem_title = resolve_header_from_stem(
                    rule_file.stem, section_globs if section_globs else {}
                )
                if desc and desc.strip().lower() not in (
                    header.strip().lower(),
                    stem_title.strip().lower(),
                ):
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

    def _extract_metadata_from_frontmatter(
        self, content: str
    ) -> tuple[str | None, str | None, bool]:
        """Extract description, glob pattern, and alwaysApply from YAML frontmatter.

        Returns:
            tuple: (description, glob_pattern, always_apply)
        """

        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None, None, False

        description = extract_frontmatter_description(lines)
        glob_pattern = None
        always_apply = False

        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == "---":
                break
            if line.startswith("alwaysApply:"):
                val = line[len("alwaysApply:") :].strip().lower()
                always_apply = val == "true"
            elif line.startswith("globs:"):
                globs_val = line[len("globs:") :].strip()
                # parse either inline list ["*.py"] or [] or list on next lines
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
                                glob_pattern = (
                                    next_line[1:].strip().strip('"').strip("'")
                                )
                                break

        return description, glob_pattern, always_apply

    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        "write a .agents rule file (.md) with YAML frontmatter"

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

    def detect(self, base_dir: Path) -> bool:
        "detect if .agents layout is in use in the given directory"

        return (base_dir / ".agents").exists()
