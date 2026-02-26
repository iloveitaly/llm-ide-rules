[![Release Notes](https://img.shields.io/github/release/iloveitaly/llm-ide-rules)](https://github.com/iloveitaly/llm-ide-rules/releases)
[![Downloads](https://static.pepy.tech/badge/llm-ide-rules/month)](https://pepy.tech/project/llm-ide-rules)
![GitHub CI Status](https://github.com/iloveitaly/llm-ide-rules/actions/workflows/build_and_publish_release_please.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Copilot, Cursor, Claude, Gemini, etc LLM Instructions

This project makes it easy to download prompts and implode/explode them so they can be used by various providers. It's completely vibe coded, but it works.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

Some of the glob assumptions in this repo are specific to how I've chosen to organize python and typescript [in the python starter template](https://github.com/iloveitaly/python-starter-template) and what tooling (fastapi, etc) that I've chosen to use.

## IDE Format Comparison

Different AI coding assistants use different formats for instructions and commands:

| IDE | type | folder | Notes |
|-----|------|--------|-------|
| **Cursor** | instructions | `.cursor/rules/*.mdc` | Multiple plain markdown files |
| **Cursor** | commands | `.cursor/commands/*.md` | Plain markdown, no frontmatter |
| **Claude Code** | instructions | `CLAUDE.md` | Single markdown file at root |
| **Claude Code** | instructions | `AGENT.md` | Single markdown file at root (agent-specific) |
| **Claude Code** | commands | `.claude/commands/*.md` | Plain markdown, no frontmatter |
| **GitHub Copilot** | instructions | `.github/copilot-instructions.md` | Single markdown file |
| **GitHub Copilot** | instructions | `.github/instructions/*.instructions.md` | Multiple instruction files |
| **GitHub Copilot** | prompts | `.github/prompts/*.prompt.md` | YAML frontmatter with `mode: 'agent'` |
| **Gemini CLI** | instructions | `AGENTS.md` | Single markdown file at root |
| **Gemini CLI** | commands | `.gemini/commands/*.toml` | TOML format, supports `{{args}}` and shell commands |
| **OpenCode** | commands | `.opencode/commands/*.md` | Plain markdown, no frontmatter |

### MCP Server Configuration

Each IDE stores MCP server configuration in a different location and format. The `mcp.json` file in this repo is a unified format that can be exploded into per-IDE configs:

| IDE | project path | global path | root key |
|-----|-------------|-------------|----------|
| **Claude Code** | `.mcp.json` | `~/.claude.json` | `mcpServers` |
| **Cursor** | `.cursor/mcp.json` | `~/.cursor/mcp.json" | `mcpServers` |
| **VS Code** | `.vscode/mcp.json` | — | `servers` |
| **GitHub Copilot** | `.copilot/mcp-config.json` | `~/.copilot/mcp-config.json` | `mcpServers` |
| **Gemini CLI** | `.gemini/settings.json` | `~/.gemini/settings.json` | `mcpServers` |
| **OpenCode** | `opencode.json` | `~/.config/opencode/opencode.json` | `mcp` |

The unified `mcp.json` format uses a `servers` top-level key:

```json
{
  "servers": {
    "my-sse-server": {
      "url": "https://example.com/mcp"
    },
    "my-streamable-http-server": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:12306/mcp"
    },
    "my-stdio-server": {
      "command": "npx",
      "args": ["my-mcp-package@latest"],
      "env": {
        "API_KEY": "..."
      }
    },
    "my-docker-server": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "my/mcp-image"]
    }
  }
}
```

Each server entry supports:
- `url` — for HTTP/SSE-based servers
- `type` — optional transport hint (e.g. `streamableHttp`); omit for default SSE
- `command` + `args` — for stdio-based servers (npx, docker, etc.)
- `env` — optional environment variables passed to the server

## Installation

```sh
uvx llm-ide-rules@latest --help
```

## Usage

### CLI Commands

The `llm-ide-rules` CLI provides commands to manage LLM IDE prompts and rules:

```sh
# Convert instruction file to separate rule files
uvx llm-ide-rules explode [input_file]

# Bundle rule files back into a single instruction file
uvx llm-ide-rules implode cursor [output_file]     # Bundle Cursor rules
uvx llm-ide-rules implode github [output_file]     # Bundle GitHub/Copilot instructions
uvx llm-ide-rules implode claude [output_file]     # Bundle Claude Code commands
uvx llm-ide-rules implode gemini [output_file]     # Bundle Gemini CLI commands
uvx llm-ide-rules implode opencode [output_file]   # Bundle OpenCode commands

# Download instruction files from repositories
uvx llm-ide-rules download [instruction_types]    # Download everything by default
uvx llm-ide-rules download cursor github          # Download specific types
uvx llm-ide-rules download --repo other/repo      # Download from different repo

# Delete downloaded instruction files
uvx llm-ide-rules delete [instruction_types]      # Delete everything by default
uvx llm-ide-rules delete cursor gemini            # Delete specific types
uvx llm-ide-rules delete --yes                    # Skip confirmation prompt

# Manage MCP server configurations
uvx llm-ide-rules mcp explode [mcp.json]          # Explode unified config to per-IDE files
uvx llm-ide-rules mcp explode --agent claude      # Explode for a specific agent only
uvx llm-ide-rules mcp explode --scope global      # Write to global config paths
uvx llm-ide-rules mcp explode --scope both        # Write to both project and global paths
uvx llm-ide-rules mcp implode --source claude     # Merge agent config back to mcp.json
uvx llm-ide-rules mcp implode --source cursor --scope global  # Read from global config
```

### Authentication

To avoid GitHub API rate limits or to access private repositories, you can set the `GITHUB_TOKEN` environment variable. The `download` command will automatically use this token for authentication.

```sh
export GITHUB_TOKEN=your_token_here
uvx llm-ide-rules download
```

### Examples

```sh
# Explode instructions.md into all supported formats (cursor, github, claude, gemini, opencode)
uvx llm-ide-rules explode instructions.md

# Explode for a specific agent only
uvx llm-ide-rules explode instructions.md --agent opencode

# Bundle Cursor rules back into a single file
uvx llm-ide-rules implode cursor bundled-instructions.md

# Bundle GitHub instructions with verbose logging
uvx llm-ide-rules implode github --verbose instructions.md

# Bundle OpenCode commands into commands.md
uvx llm-ide-rules implode opencode

# Download everything from default repository
uvx llm-ide-rules download

# Download only specific instruction types
uvx llm-ide-rules download cursor github

# Download from a different repository
uvx llm-ide-rules download --repo other-user/other-repo --target ./my-project

# Delete all downloaded files (with confirmation)
uvx llm-ide-rules delete

# Delete specific instruction types
uvx llm-ide-rules delete cursor gemini --target ./my-project

# Delete without confirmation prompt
uvx llm-ide-rules delete --yes

# Explode mcp.json to all supported IDE formats
uvx llm-ide-rules mcp explode

# Explode mcp.json to Claude Code only
uvx llm-ide-rules mcp explode --agent claude

# Explode to both project and global config paths
uvx llm-ide-rules mcp explode --scope both

# Pull Claude's project MCP config back into unified mcp.json
uvx llm-ide-rules mcp implode --source claude
```

## Extracting Changes

The idea of this repo is you'll copy prompts into your various projects. Then, if you improve a prompt in a project, you can pull that change into this upstream repo.

Here's how to do it:

```shell
git diff .github/instructions | pbcopy
pbpaste | gpatch -p1
```

`gpatch` is an updated version of patch on macOS that seems to work much better for me.

## Related Links

* https://cursor.directory/rules
* https://github.com/PatrickJS/awesome-cursorrules
* https://www.cursorprompts.org

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
