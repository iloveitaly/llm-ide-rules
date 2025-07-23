# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

Some of the glob assumptions in this repo are specific to how I've chosen to organize python and typescript [in the python starter template](https://github.com/iloveitaly/python-starter-template) and what tooling (fastapi, etc) that I've chosen to use.

## Usage

You can then download the rules into your project:

```sh
# Download .cursor rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/download.sh | sh -s cursor

# Download .github rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/download.sh | sh -s github
```

## MCP Configuration Management

This repo includes `mcp.cli`, a tool for managing MCP (Model Context Protocol) configurations across different IDEs:

```sh
# Convert generic mcp.json to VS Code and Cursor formats
python3 mcp.cli explode mcp.json

# Convert VS Code format back to generic
python3 mcp.cli implode vscode

# Convert Cursor format back to generic  
python3 mcp.cli implode cursor

# Analyze any MCP configuration file
python3 mcp.cli info mcp.json
```

See [MCP_CLI_README.md](MCP_CLI_README.md) for detailed usage and examples.

## Development

All instructions in [instructions.md](instructions.md) are exploded out into the various files with default rules applied.

```shell
just build
```

Executes this explosion process.


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
