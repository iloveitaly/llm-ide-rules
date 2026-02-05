## Standalone Python Scripts

Use this header:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
```

- Specify dependencies via the `dependencies` variable in the above comment
- Do not install packages with pip or any other package manager, assume packages will be installed when needed using `uv run --script`.
- Use `click` for CLI interfaces
- When listing constants at the top of the file, include a newline between entries and (for non-obvious constants) document each constant with a comment:

```python
# matches full lowercase git shas (short or full)
SHA_REGEX = re.compile(r"^[0-9a-f]{7,40}$")

# matches any char not allowed in dns labels
SAFE_CHARS_REGEX = re.compile(r"[^a-z0-9-]")

DEFAULT_ENVIRONMENT_NAME = "production"
DEFAULT_SERVICE_NAME = "Postgres"
```

### CLI Output and Logging

- Use `structlog_config` for logging. Read the usage guide: @https://github.com/iloveitaly/structlog-config/
- Use logging for operational/debugging info that goes to structured logs.
- Use CLI output for user-facing messages the user needs to see during normal execution (status updates, warnings, errors). Color these messages.
