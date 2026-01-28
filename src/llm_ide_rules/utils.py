"""Utility functions for LLM IDE rules."""

import re
from pathlib import Path


def modify_json_file(file_path: Path, updates: dict[str, any]) -> bool:
    """Modify a JSON/JSONC file by adding MISSING keys using string manipulation to preserve comments.
    
    Returns:
        bool: True if changes were written to the file, False otherwise.
    """
    if not file_path.exists():
        # Create new file with standard JSON if it doesn't exist
        import json

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(updates, indent=2))
        return True

    original_content = file_path.read_text()
    content = original_content

    for key, value in updates.items():
        # Prepare the value representation (basic JSON serialization)
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, str):
            val_str = f'"{value}"'
        else:
            import json

            val_str = json.dumps(value)

        # Updated pattern:
        # 1. Match key part: (["']?key["']?\s* : \s*)
        # 2. Match value part: ([^,\n\r}]+?)
        # 3. Lookahead to stop before a comma, newline, closing brace, or start of a comment
        escaped_key = re.escape(key)
        pattern_str = (
            rf'(["\\]?{escaped_key}["\\]?\s*:\s*)([^,\n\r}}]+?)'
            r'(?=\s*(?:,|\n|\r|\}|\/\/|\/\*))'
        )
        pattern = re.compile(pattern_str, re.MULTILINE)

        match = pattern.search(content)
        if match:
            # Key already exists, do NOT modify it per user instructions
            continue
        else:
            # Insert new key
            last_brace_idx = content.rfind("}")
            if last_brace_idx != -1:
                insertion_point = last_brace_idx

                # Look backwards for the first non-whitespace character before the brace
                prev_char_idx = insertion_point - 1
                while prev_char_idx >= 0 and content[prev_char_idx].isspace():
                    prev_char_idx -= 1

                # Detect indentation from the previous line if possible
                line_start = content.rfind("\n", 0, insertion_point)
                if line_start != -1:
                    indent_match = re.match(r"^(\s*)", content[line_start + 1 :])
                    indent = indent_match.group(1) if indent_match else "  "
                else:
                    indent = "  "

                if prev_char_idx >= 0:
                    prev_char = content[prev_char_idx]
                    # If the last thing wasn't a comma or opening brace, we need a comma
                    if prev_char not in ["{", ","]:
                        new_entry = f',\n{indent}\"{key}\": {val_str}'
                    else:
                        new_entry = f'\n{indent}\"{key}\": {val_str}'

                    content = (
                        content[:insertion_point]
                        + new_entry
                        + content[insertion_point:]
                    )

        if content != original_content:

            file_path.write_text(content)

            return True

        

        return False

    