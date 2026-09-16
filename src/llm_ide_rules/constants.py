"""Shared constants for explode and implode functionality."""

VALID_AGENTS = [
    "cursor",
    "github",
    "claude",
    "opencode",
    "agents",
    "antigravity",
    "grok",
    "all",
]


def parse_client_names(value: str | list[str] | None) -> list[str]:
    """Split comma-separated client names, preserving order and dropping empties."""
    if value is None:
        return []

    raw_values = [value] if isinstance(value, str) else list(value)
    clients: list[str] = []
    for raw in raw_values:
        for client in raw.split(","):
            client = client.strip()
            if client:
                clients.append(client)

    return list(dict.fromkeys(clients))


def header_to_filename(header: str) -> str:
    """Convert a section header to a filename."""
    return header.lower().replace(" ", "-")


def filename_to_header(filename: str) -> str:
    """Convert a filename back to a section header."""
    return filename.replace("-", " ").title()
