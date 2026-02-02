"""Test splitting AGENTS.md based on globs."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_agents_splitting_basic():
    """Test that rules are split into different AGENTS.md files based on globs."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create directories
        Path("frontend/src").mkdir(parents=True)
        Path("backend/app").mkdir(parents=True)

        instructions_content = """# General Instructions
These are general instructions.

## Frontend
globs: frontend/src/**/*.ts
Frontend specific rules.

## Backend
globs: backend/app/**/*.py
Backend specific rules.

## RootRule
globs: *.md
Root level rules.

## AlwaysApply
Always apply rules.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "agents"])

        assert result.exit_code == 0

        # Check root AGENTS.md
        root_agents = Path("AGENTS.md")
        assert root_agents.exists()
        root_content = root_agents.read_text()
        assert "These are general instructions." in root_content
        assert "## RootRule" in root_content
        assert "## AlwaysApply" in root_content
        assert "## Frontend" not in root_content
        assert "## Backend" not in root_content

        # Check frontend AGENTS.md
        frontend_agents = Path("frontend/src/AGENTS.md")
        assert frontend_agents.exists()
        frontend_content = frontend_agents.read_text()
        assert "These are general instructions." not in frontend_content
        assert "## Frontend" in frontend_content
        assert "Frontend specific rules." in frontend_content
        assert "## Backend" not in frontend_content

        # Check backend AGENTS.md
        backend_agents = Path("backend/app/AGENTS.md")
        assert backend_agents.exists()
        backend_content = backend_agents.read_text()
        assert "These are general instructions." not in backend_content
        assert "## Backend" in backend_content
        assert "Backend specific rules." in backend_content


def test_agents_splitting_fallback():
    """Test that rules fallback to nearest existing directory if target doesn't exist."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create parent directory but not deep directory
        Path("src").mkdir()

        instructions_content = """# General Instructions
General.

## DeepRule
globs: src/deep/missing/dir/**/*.ts
Should fall back to src/.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "agents"])

        assert result.exit_code == 0

        # Should be in src/AGENTS.md because src/ exists but src/deep/missing/dir does not
        src_agents = Path("src/AGENTS.md")
        assert src_agents.exists()
        content = src_agents.read_text()
        assert "## DeepRule" in content

        # Should not be in root
        root_agents = Path("AGENTS.md")
        if root_agents.exists():
            root_content = root_agents.read_text()
            assert "## DeepRule" not in root_content


def test_agents_splitting_complex_globs():
    """Test splitting with multiple rules targeting same directory."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        Path("lib").mkdir()

        instructions_content = """# General
General.

## Rule1
globs: lib/**/*.js
Rule 1.

## Rule2
globs: lib/**/*.ts
Rule 2.
"""

        Path("instructions.md").write_text(instructions_content)

        result = runner.invoke(app, ["explode", "instructions.md", "--agent", "agents"])

        assert result.exit_code == 0

        lib_agents = Path("lib/AGENTS.md")
        assert lib_agents.exists()
        content = lib_agents.read_text()
        assert "## Rule1" in content
        assert "## Rule2" in content
