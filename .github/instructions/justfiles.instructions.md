---
applyTo: "just/*.just"
---
## Justfiles


- Never use `just_executable()` to reference the executable for `just`. If `just` DNE, then something is wrong adn you should stop your work and let me know.
- You should not have to mutate `$PATH`. If you cannot find an expected binary, stop your work and let me know.
- Do not create aliases unless explicitly asked
- Separate scripts larger than 5 lines with newlines and comments for non-obvious logic
- Do not use inline shebang unless it differs from the default

Use the following script execution configuration:

```
# zsh is the default shell under macos, let's mirror it everywhere
set shell := ["zsh", "-ceuB", "-o", "pipefail", "-o", "extended_glob"]

# determines what shell to use for [script]
set script-interpreter := ["zsh", "-euB", "-o", "pipefail", "-o", "extended_glob"]
```
