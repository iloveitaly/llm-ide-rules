"base agent class and shared utilities for LLM IDE rules"

from abc import ABC, abstractmethod
from pathlib import Path

from llm_ide_rules.constants import header_to_filename
from llm_ide_rules.utils import preserve_custom_content


class BaseAgent(ABC):
    "base class for all IDE agents"

    name: str
    rules_dir: str | None = None
    commands_dir: str | None = None
    rule_extension: str | None = None
    command_extension: str | None = None

    @abstractmethod
    def bundle_rules(
        self,
        output_file: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> bool:
        "bundle rule files into a single output file"
        ...

    @abstractmethod
    def bundle_commands(
        self, output_file: Path, section_globs: dict[str, str | None] | None = None
    ) -> bool:
        "bundle command files into a single output file"
        ...

    @abstractmethod
    def write_rule(
        self,
        content_lines: list[str],
        filename: str,
        rules_dir: Path,
        glob_pattern: str | None = None,
        description: str | None = None,
    ) -> None:
        "write a single rule file"
        ...

    @abstractmethod
    def write_command(
        self,
        content_lines: list[str],
        filename: str,
        commands_dir: Path,
        section_name: str | None = None,
    ) -> None:
        "write a single command file"
        ...

    def detect(self, base_dir: Path) -> bool:
        "detect if this agent is in use in the given directory"

        return False

    def configure_agents_md(self, base_dir: Path) -> bool:
        """Configure the agent to use AGENTS.md as context (default: no-op).

        Returns:
            bool: True if configuration was applied, False otherwise.
        """

        return False

    def generate_root_doc(
        self,
        general_lines: list[str],
        rules_sections: dict[str, list[str]],
        command_sections: dict[str, list[str]],
        output_dir: Path,
        section_globs: dict[str, str | None] | None = None,
        filename: str = "AGENTS.md",
    ) -> None:
        "generate a root documentation file (e.g. CLAUDE.md) if supported"

        return

    def build_root_doc_content(
        self,
        general_lines: list[str],
        rules_sections: dict[str, list[str]],
    ) -> str:
        "build the content string for a root documentation file by aggregating rules"

        content = []

        # add general instructions
        if general_lines:
            trimmed = trim_content(general_lines)
            if trimmed:
                content.extend(trimmed)
                content.append("\n\n")

        # add sections in document order
        for lines in rules_sections.values():
            trimmed = trim_content(lines)
            if trimmed:
                content.extend(trimmed)
                content.append("\n\n")

        return "".join(content).strip() + "\n" if content else ""

    def get_rules_path(self, base_dir: Path) -> Path:
        "get the full path to the rules directory"

        if not self.rules_dir:
            raise NotImplementedError(f"{self.name} does not support rules")
        return base_dir / self.rules_dir

    def get_commands_path(self, base_dir: Path) -> Path:
        "get the full path to the commands directory"

        if not self.commands_dir:
            raise NotImplementedError(f"{self.name} does not support commands")
        return base_dir / self.commands_dir

    def _write_bundled_content(self, output_file: Path, content: str) -> None:
        "write bundled content to output file, preserving custom instructions after marker"

        local_content = ""
        if output_file.exists():
            try:
                local_content = output_file.read_text(encoding="utf-8")
            except OSError:
                pass

        file_content = preserve_custom_content(content, local_content)
        output_file.write_text(file_content, encoding="utf-8")


def extract_frontmatter_description(lines: list[str]) -> str | None:
    "extract description from YAML frontmatter lines, supporting multiline/folded scalars"

    if not lines or lines[0].strip() != "---":
        return None

    for i in range(1, len(lines)):
        line = lines[i].strip()
        if line == "---":
            break
        if line.startswith("description:"):
            raw_val = line[len("description:") :].strip().strip('"').strip("'")
            if raw_val in (">-", ">", "|", "|-", ""):
                desc_lines = []
                for j in range(i + 1, len(lines)):
                    next_raw = lines[j]
                    stripped = next_raw.strip()
                    if stripped == "---":
                        break
                    if next_raw and not next_raw[0].isspace() and ":" in stripped:
                        break
                    if stripped:
                        desc_lines.append(stripped)
                if raw_val in ("|", "|-"):
                    return "\n".join(desc_lines)
                return " ".join(desc_lines)
            return raw_val

    return None


def strip_yaml_frontmatter(text: str) -> str:
    "strip YAML frontmatter from text"

    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :]).lstrip("\n")
    return text


def strip_header(text: str) -> str:
    "remove the first markdown header (## Header) from text if present"

    lines = text.splitlines()
    if lines and lines[0].startswith("## "):
        remaining_lines = lines[1:]
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines = remaining_lines[1:]
        return "\n".join(remaining_lines)
    return text


def _file_sort_key(p: Path) -> str:
    return p.parent.name if p.name == "SKILL.md" else p.name


def _file_stem_key(p: Path) -> str:
    return p.parent.name if p.name == "SKILL.md" else p.stem


def get_ordered_files(
    file_list: list[Path], section_globs_keys: list[str] | None = None
) -> list[Path]:
    """Order files based on section_globs key order, with unmapped files at the end.

    If section_globs_keys is None, returns files sorted alphabetically.
    """

    if not section_globs_keys:
        return sorted(file_list, key=_file_sort_key)

    file_dict = {_file_stem_key(f): f for f in file_list}
    ordered_files = []

    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    remaining_files = sorted(file_dict.values(), key=_file_sort_key)
    ordered_files.extend(remaining_files)

    return ordered_files


def _github_name_key(p: Path) -> str:
    return p.name


def get_ordered_files_github(
    file_list: list[Path], section_globs_keys: list[str] | None = None
) -> list[Path]:
    """Order GitHub instruction files, handling .instructions suffix.

    If section_globs_keys is None, returns files sorted alphabetically.
    """

    if not section_globs_keys:
        return sorted(file_list, key=_github_name_key)

    file_dict = {}
    for f in file_list:
        base_stem = f.stem.replace(".instructions", "")
        file_dict[base_stem] = f

    ordered_files = []

    for section_name in section_globs_keys:
        filename = header_to_filename(section_name)
        if filename in file_dict:
            ordered_files.append(file_dict[filename])
            del file_dict[filename]

    remaining_files = sorted(file_dict.values(), key=_github_name_key)
    ordered_files.extend(remaining_files)

    return ordered_files


def resolve_header_from_stem(stem: str, section_globs: dict[str, str | None]) -> str:
    """Return the canonical header for a given filename stem.

    Prefer exact header names from section_globs (preserves acronyms like FastAPI, TypeScript).
    Fallback to title-casing the filename when not found in section_globs.
    """

    for section_name in section_globs:
        if header_to_filename(section_name) == stem:
            return section_name

    return stem.replace("-", " ").title()


def trim_content(content_lines: list[str]) -> list[str]:
    "remove leading and trailing empty lines from content"

    start = 0
    for i, line in enumerate(content_lines):
        if line.strip():
            start = i
            break
    else:
        return []

    end = len(content_lines)
    for i in range(len(content_lines) - 1, -1, -1):
        if content_lines[i].strip():
            end = i + 1
            break

    return content_lines[start:end]


def write_rule_file(path: Path, header_yaml: str, content_lines: list[str]) -> None:
    "write a rule file with front matter and content"

    trimmed_content = trim_content(content_lines)
    output = header_yaml.strip() + "\n" + "".join(trimmed_content)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output)


def replace_header_with_proper_casing(
    content_lines: list[str], proper_header: str
) -> list[str]:
    "replace the first header in content with the properly cased version"

    if not content_lines:
        return content_lines

    for i, line in enumerate(content_lines):
        if line.startswith("## "):
            content_lines[i] = f"## {proper_header}\n"
            break

    return content_lines


def extract_description_and_filter_content(
    content_lines: list[str], default_description: str
) -> tuple[str, list[str]]:
    "extract description from first non-empty line that starts with 'Description:' and return filtered content"

    trimmed_content = trim_content(content_lines)
    description = ""
    description_line = None

    for i, line in enumerate(trimmed_content):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue

        if stripped_line.startswith("Description:"):
            description = stripped_line[len("Description:") :].strip()
            description_line = i
        break

    if description and description_line is not None:
        end_idx = description_line + 1
        if description_line > 0 and not trimmed_content[description_line - 1].strip():
            while (
                end_idx < len(trimmed_content) and not trimmed_content[end_idx].strip()
            ):
                end_idx += 1
        filtered_content = (
            trimmed_content[:description_line] + trimmed_content[end_idx:]
        )
        filtered_content = trim_content(filtered_content)
    else:
        filtered_content = trimmed_content

    return description, filtered_content
