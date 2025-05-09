# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

## Usage

You can then download the rules into your project:

```sh
# Download .cursor rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/install.sh | sh -s cursor

# Download .github rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/install.sh | sh -s github
```

## Development

All instructions in [[instructions.md]] are exploded out into the various files with default rules applied.

```shell
just build
```

Executes this explosion process.