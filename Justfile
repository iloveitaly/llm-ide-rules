# Justfiles are nicer, and now we're using one!


# Set up the Python environment
setup:
    uv sync
    @echo "activate: source ./.venv/bin/activate"

# Build the package
build:
    uv build



test:
    pytest

# Generate database schema prompt (requires DATABASE_URL environment variable)
db_prompt *ARGS:
    #!/usr/bin/env bash
    if [ -z "$DATABASE_URL" ]; then
        echo "Error: DATABASE_URL environment variable must be set"
        exit 1
    fi
    uvx --from . airules db-prompt "$DATABASE_URL" {{ARGS}}



# Clean build artifacts and cache
clean:
    rm -rf *.egg-info .venv dist/
    find . -type d -name "__pycache__" -prune -exec rm -rf {} \; 2>/dev/null || true

# Update copier template
update_copier:
    uv tool run --with jinja2_shell_extension \
        copier@latest update --vcs-ref=HEAD --trust --skip-tasks --skip-answered
