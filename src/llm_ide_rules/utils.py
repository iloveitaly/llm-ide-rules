"Utility functions for LLM IDE rules."

import re
from pathlib import Path


def modify_json_file(file_path: Path, updates: dict[str, any]) -> None:
    """Modify a JSON/JSONC file by updating or adding keys using string manipulation to preserve comments."""
    if not file_path.exists():
        # Create new file with standard JSON if it doesn't exist
        import json
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(updates, indent=2))
        return

    content = file_path.read_text()
    
    for key, value in updates.items():
        # Prepare the value representation (basic JSON serialization)
        if isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, str):
            val_str = f'"{value}"'
        else:
            # Fallback for complex types (not fully supported by this simple regex replacer)
            import json
            val_str = json.dumps(value)

        # Regex to find "key": ...
        # Handles optional quotes around key, spacing, and value capturing
        # Note: This regex is simplistic and assumes keys are unique and simple.
        # It handles "key" : value or "key": value
        pattern = re.compile(rf'([""]?{re.escape(key)}[""]?\s*:\s*)([^,\n}}]+)', re.MULTILINE)
        
        match = pattern.search(content)
        if match:
            # Update existing key
            # Check if value is actually different to avoid unnecessary writes
            current_val = match.group(2).strip().rstrip(',')
            if current_val != val_str:
                # We carefully replace only the value group
                # match.group(1) is the key part ("key": )
                # match.group(2) is the value part (false / "foo")
                # We need to handle trailing commas in the original value if captured?
                # The regex ([^,\n}}]+) stops at comma or newline or brace.
                # So we just replace the group 2 range.
                start, end = match.span(2)
                # Check if original had a trailing comma captured (unlikely with our regex)
                content = content[:start] + val_str + content[end:]
        else:
            # Insert new key
            # Find the last closing brace '}'
            last_brace_idx = content.rfind('}')
            if last_brace_idx != -1:
                # Check if there is a trailing comma on the previous element
                # Scan backwards from brace ignoring whitespace/comments?
                # This is hard with regex. 
                # simplified approach: insert at end, ensure comma on previous line if needed.
                
                # Find the insertion point (before the last brace)
                insertion_point = last_brace_idx
                
                # Look backwards for non-whitespace
                prev_char_idx = insertion_point - 1
                while prev_char_idx >= 0 and content[prev_char_idx].isspace():
                    prev_char_idx -= 1
                
                prefix = ""
                if prev_char_idx >= 0 and content[prev_char_idx] not in ['{', ',', '[']:
                    # Previous element likely needs a comma
                    # But wait, what if it's a comment? 
                    # Providing robust insertion in JSONC without a parser is extremely hard.
                    # Assumption: User follows standard formatting.
                    # We will append a comma to the previous non-whitespace char if it's not a comma/brace.
                    # Actually, inserting a comma might break comments (e.g. // comment ,)
                    
                    # Safer approach for insertion:
                    # 1. Try to find the last property.
                    # 2. Append comma to it.
                    # 3. Add new line.
                    
                    # Let's try a simpler append strategy:
                    # Just insert ",\n  "key": value" before the last brace.
                    # If it was empty object {}, we clean up the comma.
                    pass

                # Basic indentation detection
                indent = "  "
                
                to_insert = f',\n{indent}"{key}": {val_str}'
                
                # Handle empty object case specially
                if content[prev_char_idx] == '{':
                    to_insert = f'\n{indent}"{key}": {val_str}\n'
                
                content = content[:insertion_point] + to_insert + content[insertion_point:]

    file_path.write_text(content)
