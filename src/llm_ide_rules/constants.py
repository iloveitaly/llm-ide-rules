"""Shared constants for explode and implode functionality."""

VALID_AGENTS = [
    "cursor",
    "github",
    "claude",
    "opencode",
    "agents",
    "antigravity",
    "grok",
    "codex",
    "all",
]

EXPLODE_AGENTS = [name for name in VALID_AGENTS if name != "all"]

# Standing rules live in AGENTS.md rather than a vendor-specific rules dir
AGENTS_MD_CLIENTS = frozenset({"opencode", "codex"})

# Clients that explode into the shared .agents layout
DOTAGENTS_LAYOUT_CLIENTS = frozenset({"antigravity", "grok", "codex"})

# Share .agents/ with antigravity, so skip them from download/delete defaults
SHARED_DOTAGENTS_DEFAULT_EXCLUDES = frozenset({"grok", "codex"})


def ensure_agents_adapter(agent_names: list[str]) -> list[str]:
    """Append the AGENTS.md adapter when a client stores standing rules there."""
    if "agents" in agent_names:
        return list(agent_names)

    if any(name in AGENTS_MD_CLIENTS for name in agent_names):
        return [*agent_names, "agents"]

    return list(agent_names)


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
