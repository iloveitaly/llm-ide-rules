# Copilot & Cursor LLM Instructions

Going to try to centralize all my prompts in a single place and create some scripts to help convert from copilot to cursor, etc.

I don't want to be tied to a specific IDE and it's a pain to have to edit instructions for various languages across a ton of different files.

Additionally, it becomes challenging to copy these prompts into various projects and contribute them back to a single location.

## Usage

You can then download the rules into your project:

```sh
# Download .cursor rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/install.sh | sh -s cursor

# Download .github rules
curl -sSL https://raw.githubusercontent.com/iloveitaly/llm-ide-prompts/master/install.sh | sh -s github
```

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