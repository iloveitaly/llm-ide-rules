# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

Some of the glob assumptions in this repo are specific to how I've chosen to organize python and typescript [in the python starter template](https://github.com/iloveitaly/python-starter-template) and what tooling (fastapi, etc) that I've chosen to use.

## Installation

You can run the `airules` CLI tool using uvx:

```sh
uvx airules
```

Or install from the repository:

```sh
uv tool install git+https://github.com/iloveitaly/airules.git
```

```sh
git clone https://github.com/iloveitaly/airules.git
cd airules
uv sync
source .venv/bin/activate
```

## Usage

### CLI Commands

The `airules` CLI provides commands to manage LLM IDE prompts and rules:

```sh
# Convert instruction file to separate rule files
uvx airules explode [input_file]

# Bundle rule files back into a single instruction file
uvx airules implode cursor [output_file]     # Bundle Cursor rules
uvx airules implode github [output_file]    # Bundle GitHub/Copilot instructions

# Download instruction files from repositories
uvx airules download [instruction_types]    # Download everything by default
uvx airules download cursor github          # Download specific types
uvx airules download --repo other/repo      # Download from different repo

# Generate database schema prompts
uvx airules db-prompt [DATABASE_URL]        # Generate schema prompt from database


```

### Examples

```sh
# Explode instructions.md into .cursor/rules/ and .github/instructions/
uvx airules explode instructions.md

# Bundle Cursor rules back into a single file
uvx airules implode cursor bundled-instructions.md

# Bundle GitHub instructions with verbose logging
uvx airules implode github --verbose instructions.md

# Download everything from default repository
uvx airules download

# Download only specific instruction types
uvx airules download cursor github

# Download from a different repository
uvx airules download --repo other-user/other-repo --target ./my-project

# Generate database schema prompt (requires DATABASE_URL)
uvx airules db-prompt "postgresql://user:pass@localhost/mydb" --all
uvx airules db-prompt "postgresql://user:pass@localhost/mydb" --table users --table products
uvx airules db-prompt "postgresql://user:pass@localhost/mydb" --include-data
```

## Development

### Using the CLI for Development

The CLI replaces the old standalone scripts. Use the CLI commands in your development workflow:

```shell
# Setup the environment
uv sync

# Explode instructions into separate rule files
uvx airules explode

# Bundle rules back into instructions
uvx airules implode cursor instructions.md

# Generate database schema prompt using just
just db_prompt --all
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
