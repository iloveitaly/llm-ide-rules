"utility functions for LLM IDE rules"

import re
from collections.abc import Mapping
from pathlib import Path

from llm_ide_rules.constants import COMMANDS_MARKER, INSTRUCTIONS_MARKER


def modify_json_file(file_path: Path, updates: Mapping[str, object]) -> bool:
    """Modify a JSON/JSONC file by adding MISSING keys using string manipulation to preserve comments.

    Returns:
        bool: True if changes were written to the file, False otherwise.
    """

    if not file_path.exists():
        # create new file with standard json if it doesn't exist
        import json

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(updates, indent=2))
        return True

    original_content = file_path.read_text()
    content = original_content

    for key, value in updates.items():
        # prepare the value representation (basic json serialization)
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, str):
            val_str = f'"{value}"'
        else:
            import json

            val_str = json.dumps(value)

        escaped_key = re.escape(key)
        # capture key prefix and value while stopping before boundary delimiters
        pattern = re.compile(
            rf"""
            (                   # capture group 1: key part with optional quotes and colon
                ["']?           # optional quote before key
                {escaped_key}   # escaped key name
                ["']?           # optional quote after key
                \s*:\s*         # colon separator with optional whitespace
            )
            (                   # capture group 2: value part
                [^,\n\r}}]+?    # value characters up to boundary delimiter
            )
            (?=                 # positive lookahead boundary
                \s*             # optional whitespace
                (?:,|\n|\r|\}}|\/\/|\/\*) # stop before comma, newline, closing brace, or comment
            )
            """,
            re.VERBOSE | re.MULTILINE,
        )

        match = pattern.search(content)
        if match:
            # key exists, replace the value part
            key_part = match.group(1)
            # replace the value part (group 2) with new value
            new_entry = f"{key_part}{val_str}"
            content = content[: match.start()] + new_entry + content[match.end() :]
        else:
            # insert new key
            last_brace_idx = content.rfind("}")
            if last_brace_idx != -1:
                insertion_point = last_brace_idx

                # look backwards for the first non-whitespace character before the brace
                prev_char_idx = insertion_point - 1
                while prev_char_idx >= 0 and content[prev_char_idx].isspace():
                    prev_char_idx -= 1

                # detect indentation from the previous line if possible
                line_start = content.rfind("\n", 0, insertion_point)
                if line_start != -1:
                    indent_pattern = re.compile(
                        r"""
                        ^       # start of line
                        (\s*)   # leading whitespace indentation
                        """,
                        re.VERBOSE,
                    )
                    indent_match = indent_pattern.match(content[line_start + 1 :])
                    indent = indent_match.group(1) if indent_match else "  "
                else:
                    indent = "  "

                if prev_char_idx >= 0:
                    prev_char = content[prev_char_idx]
                    # if the last thing wasn't a comma or opening brace, we need a comma
                    if prev_char not in ["{", ","]:
                        new_entry = f',\n{indent}"{key}": {val_str}'
                    else:
                        new_entry = f'\n{indent}"{key}": {val_str}'

                    content = (
                        content[:insertion_point]
                        + new_entry
                        + content[insertion_point:]
                    )

    if content != original_content:
        file_path.write_text(content)
        return True

    return False


def resolve_target_dir(base_dir: Path, glob_pattern: str | None) -> Path:
    "resolve the target directory for a glob pattern by finding the deepest existing directory"

    if not glob_pattern or "**" not in glob_pattern:
        return base_dir

    prefix = glob_pattern.split("**")[0].strip("/")
    potential_dir = base_dir / prefix

    check_dir = potential_dir
    while not check_dir.exists() and check_dir != base_dir:
        check_dir = check_dir.parent

    return check_dir


def find_project_root(start_path: Path | None = None) -> Path:
    "find the project root by looking for common markers"

    if start_path is None:
        start_path = Path.cwd()

    path = start_path.resolve()
    # check current directory and parents
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return parent
        if (parent / "pyproject.toml").exists():
            return parent
        if (parent / ".cursor").exists():
            return parent
        if (parent / ".claude").exists():
            return parent
        if (parent / ".github").exists():
            return parent

    # fallback to current directory
    return start_path


def preserve_custom_content(
    base_content: str,
    existing_content: str,
    default_marker: str = INSTRUCTIONS_MARKER,
) -> str:
    "combine base content with preserved custom content from existing file"

    marker = default_marker
    if default_marker not in existing_content and COMMANDS_MARKER in existing_content:
        marker = COMMANDS_MARKER

    local_custom_content = ""
    if marker in existing_content:
        local_custom_content = existing_content.split(marker, 1)[1]
    elif default_marker in existing_content:
        local_custom_content = existing_content.split(default_marker, 1)[1]

    # strip any marker already present in base_content
    if marker in base_content:
        base_content = base_content.split(marker, 1)[0]
    if default_marker in base_content:
        base_content = base_content.split(default_marker, 1)[0]
    if COMMANDS_MARKER in base_content:
        base_content = base_content.split(COMMANDS_MARKER, 1)[0]

    cleaned_base = base_content.rstrip()
    custom_content = local_custom_content.strip()

    base_part = f"{cleaned_base}\n\n{marker}\n" if cleaned_base else f"{marker}\n"
    if custom_content:
        return f"{base_part}\n{custom_content}\n"

    return base_part
