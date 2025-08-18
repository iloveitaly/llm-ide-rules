# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

Some of the glob assumptions in this repo are specific to how I've chosen to organize python and typescript [in the python starter template](https://github.com/iloveitaly/python-starter-template) and what tooling (fastapi, etc) that I've chosen to use.

## Installation

You can install the `llm-rules` CLI tool using uv:

```sh
uv tool install git+https://github.com/iloveitaly/llm-ide-prompts.git
```

Or install directly from the repository:

```sh
git clone https://github.com/iloveitaly/llm-ide-prompts.git
cd llm-ide-prompts
uv sync
source .venv/bin/activate
```

## Usage

### CLI Commands

The `llm-rules` CLI provides commands to manage LLM IDE prompts and rules:

```sh
# Convert instruction file to separate rule files
llm-rules explode [input_file]

# Bundle rule files back into a single instruction file
llm-rules implode cursor [output_file]     # Bundle Cursor rules
llm-rules implode github [output_file]    # Bundle GitHub/Copilot instructions

# MCP (Model Context Protocol) commands (coming soon)
llm-rules mcp status
llm-rules mcp configure
```

### Examples

```sh
# Explode instructions.md into .cursor/rules/ and .github/instructions/
llm-rules explode instructions.md

# Bundle Cursor rules back into a single file
llm-rules implode cursor bundled-instructions.md

# Bundle GitHub instructions with verbose logging
llm-rules implode github --verbose instructions.md
```

### Direct Download (Legacy)

You can also download the rules directly into your project:

```sh
# Download .cursor rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/download.sh | sh -s cursor

# Download .github rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/download.sh | sh -s github

# Download AGENT.md (for Amp)
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/AGENT.md > AGENT.md
```

## Development

### Using the CLI for Development

The CLI replaces the old standalone scripts. Use the CLI commands in your development workflow:

```shell
# Setup the environment
uv sync

# Explode instructions into separate rule files
llm-rules explode

# Bundle rules back into instructions
llm-rules implode cursor instructions.md
```

### Building and Testing

```shell
# Build the package
uv build

# Run tests
pytest
```

### Legacy Scripts (Deprecated)

The old `explode.py` and `implode.py` scripts are now deprecated in favor of the `llm-rules` CLI.


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
