# Justfiles are nicer, and now we're using one!


# Set up the Python environment
setup:
    uv sync
    @echo "activate: source ./.venv/bin/activate"

# Build the package
build:
    uv build

# Explode instructions into rule files
explode:
    llm-rules explode

# Bundle cursor rules into instructions
implode-cursor:
    llm-rules implode cursor

# Bundle github instructions
implode-github:
    llm-rules implode github

# Run tests
test:
    pytest

# Start docker services
up:
    docker compose up -d --wait

# Clean build artifacts and cache
clean:
    rm -rf *.egg-info .venv dist/
    find . -type d -name "__pycache__" -prune -exec rm -rf {} \; 2>/dev/null || true

# Update copier template
update_copier:
    uv tool run --with jinja2_shell_extension \
        copier@latest update --vcs-ref=HEAD --trust --skip-tasks --skip-answered
