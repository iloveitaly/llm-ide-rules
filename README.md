# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

Some of the glob assumptions in this repo are specific to how I've chosen to organize python and typescript [in the python starter template](https://github.com/iloveitaly/python-starter-template) and what tooling (fastapi, etc) that I've chosen to use.

## Installation

You can run the `llm-ide-rules` CLI tool using uvx:

```sh
uvx llm-ide-rules
```

Or install from the repository:

```sh
uv tool install git+https://github.com/iloveitaly/llm-ide-rules.git
```

```sh
git clone https://github.com/iloveitaly/llm-ide-rules.git
cd llm-ide-rules
uv sync
source .venv/bin/activate
```

## Usage

### CLI Commands

The `llm-ide-rules` CLI provides commands to manage LLM IDE prompts and rules:

```sh
# Convert instruction file to separate rule files
uvx llm-ide-rules explode [input_file]

# Bundle rule files back into a single instruction file
uvx llm-ide-rules implode cursor [output_file]     # Bundle Cursor rules
uvx llm-ide-rules implode github [output_file]    # Bundle GitHub/Copilot instructions

# Download instruction files from repositories
uvx llm-ide-rules download [instruction_types]    # Download everything by default
uvx llm-ide-rules download cursor github          # Download specific types
uvx llm-ide-rules download --repo other/repo      # Download from different repo


```

### Examples

```sh
# Explode instructions.md into .cursor/rules/ and .github/instructions/
uvx llm-ide-rules explode instructions.md

# Bundle Cursor rules back into a single file
uvx llm-ide-rules implode cursor bundled-instructions.md

# Bundle GitHub instructions with verbose logging
uvx llm-ide-rules implode github --verbose instructions.md

# Download everything from default repository
uvx llm-ide-rules download

# Download only specific instruction types
uvx llm-ide-rules download cursor github

# Download from a different repository
uvx llm-ide-rules download --repo other-user/other-repo --target ./my-project
```

## Development

### Using the CLI for Development

The CLI replaces the old standalone scripts. Use the CLI commands in your development workflow:

```shell
# Setup the environment
uv sync

# Explode instructions into separate rule files
uvx llm-ide-rules explode

# Bundle rules back into instructions
uvx llm-ide-rules implode cursor instructions.md
```

### Building and Testing

```shell
# Build the package
uv build

# Run tests
pytest
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
