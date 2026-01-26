"""
Pydantic models for unified MCP configuration.
"""

from pydantic import BaseModel, Field


class McpServer(BaseModel):
    """Unified MCP server definition."""

    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    type: str | None = None
    env: dict[str, str] | None = None


class McpConfig(BaseModel):
    """Unified mcp.json format."""

    servers: dict[str, McpServer]
