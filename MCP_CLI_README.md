# MCP CLI Tool

A command-line tool for converting between different MCP (Model Context Protocol) JSON configuration formats.

## Features

- **Explode**: Convert a generic MCP JSON file into VS Code and Cursor specific formats
- **Implode**: Convert VS Code or Cursor specific formats back to a generic format
- **Info**: Analyze and display information about MCP JSON files
- Support for JSON with comments (JSONC format)
- Dry-run mode to preview changes without creating files
- Automatic file format detection
- Rich terminal output with tables and colors

## Installation

The tool requires Python 3.7+ and the following dependencies:
- `typer` - CLI framework
- `rich` - Rich terminal output

```bash
pip install typer rich
```

## Usage

### Basic Commands

```bash
# Display help
python3 mcp.cli --help

# Analyze an MCP JSON file
python3 mcp.cli info mcp.json

# Convert generic MCP to VS Code and Cursor formats
python3 mcp.cli explode mcp.json

# Convert VS Code format back to generic
python3 mcp.cli implode vscode

# Convert Cursor format back to generic
python3 mcp.cli implode cursor
```

### Advanced Usage

```bash
# Explode with custom output directory
python3 mcp.cli explode mcp.json --output-dir ./configs

# Implode with custom input and output files
python3 mcp.cli implode vscode --input-file ./vscode-config.json --output-file generic.json

# Dry-run mode (preview without creating files)
python3 mcp.cli explode mcp.json --dry-run
python3 mcp.cli implode cursor --dry-run
```

## Supported Formats

### Generic Format
The standard MCP format used in this repository:
```json
{
  "servers": {
    "server-name": {
      "command": "npx",
      "args": ["@server/package"]
    }
  }
}
```

### VS Code Format
VS Code settings.json format with MCP servers under the `mcp.servers` key:
```json
{
  "mcp.servers": {
    "server-name": {
      "command": "npx", 
      "args": ["@server/package"]
    }
  }
}
```

### Cursor Format
Cursor uses a similar format to the generic format:
```json
{
  "servers": {
    "server-name": {
      "command": "npx",
      "args": ["@server/package"]
    }
  }
}
```

## Server Configuration Types

The tool supports various MCP server configuration types:

- **Command servers**: Use `command` and `args`
- **HTTP servers**: Use `url`
- **Streamable HTTP servers**: Use `type: "streamableHttp"` and `url`

## Examples

### Converting from Generic to IDE-specific

```bash
# Start with a generic mcp.json
python3 mcp.cli explode mcp.json

# Creates:
# - .vscode/settings.json (VS Code format)
# - .cursor/mcp.json (Cursor format)
```

### Converting back to Generic

```bash
# From VS Code settings
python3 mcp.cli implode vscode --output-file restored.json

# From Cursor config
python3 mcp.cli implode cursor --output-file restored.json
```

### Analysis and Debugging

```bash
# Analyze any MCP JSON file
python3 mcp.cli info .vscode/settings.json
python3 mcp.cli info .cursor/mcp.json
python3 mcp.cli info mcp.json
```

## Error Handling

The tool provides helpful error messages for:
- Missing files
- Invalid JSON syntax
- Missing required keys (`servers`, `mcp.servers`)
- Malformed configurations

## JSON with Comments Support

The tool supports JSON files with JavaScript-style comments:
```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      // This comment will be handled correctly
      "args": ["@playwright/mcp@latest", "--vision"]
    }
  }
}
```