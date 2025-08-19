"""Test explode command functionality."""

import tempfile
import shutil
import os
from pathlib import Path
from typer.testing import CliRunner

from airules import app


def test_explode_help():
    """Test that explode command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["explode", "--help"])
    assert result.exit_code == 0
    assert "Convert instruction file to separate rule files" in result.stdout
    assert "config" in result.stdout  # Look for "config" instead of "--config" to avoid ANSI styling issues


def test_explode_basic_functionality():
    """Test basic explode functionality with a sample instruction file."""
    runner = CliRunner()
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create a sample instructions.md file
        instructions_content = """# Sample Instructions

## Python

Here are Python rules for development.

## React

Here are React rules for frontend development.

## Secrets

Here are prompt rules for secrets handling.
"""
        
        with open("instructions.md", "w") as f:
            f.write(instructions_content)
        
        # Run explode command
        result = runner.invoke(app, ["explode", "instructions.md"])
        
        # Check command succeeds
        assert result.exit_code == 0
        assert "Created Cursor rules" in result.stdout
        
        # Check that directories were created
        assert Path(".cursor/rules").exists()
        assert Path(".github/instructions").exists()
        
        # Check that rule files were created
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/react.mdc").exists()
        assert Path(".cursor/rules/secrets.mdc").exists()
        
        assert Path(".github/instructions/python.instructions.md").exists()
        assert Path(".github/instructions/react.instructions.md").exists()
        
        # Check content of a rule file
        with open(".cursor/rules/python.mdc", "r") as f:
            content = f.read()
            assert "Here are Python rules for development" in content
            assert "**/*.py" in content  # Should contain the glob pattern


def test_explode_with_custom_config():
    """Test explode with custom configuration file."""
    runner = CliRunner()
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create custom config JSON
        custom_config = """{
  "section_globs": {
    "Python": "**/*.py",
    "CustomSection": "**/*.custom"
  }
}"""
        with open("custom_config.json", "w") as f:
            f.write(custom_config)
        
        # Create a sample instructions.md file
        instructions_content = """# Sample Instructions

## Python

Here are Python rules.

## CustomSection

Here are custom rules.
"""
        
        with open("instructions.md", "w") as f:
            f.write(instructions_content)
        
        # Run explode command with custom config
        result = runner.invoke(app, ["explode", "instructions.md", "--config", "custom_config.json"])
        
        # Check command succeeds
        assert result.exit_code == 0
        
        # Check that files were created according to custom config
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path(".cursor/rules/customsection.mdc").exists()


def test_explode_nonexistent_file():
    """Test explode command with nonexistent input file."""
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Run explode command with nonexistent file
        result = runner.invoke(app, ["explode", "nonexistent.md"])
        
        # Should fail gracefully
        assert result.exit_code == 1


def test_explode_verbose_option():
    """Test explode command with verbose option."""
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create a sample instructions.md file
        instructions_content = """# Sample Instructions

## Python

Here are Python rules.
"""
        
        with open("instructions.md", "w") as f:
            f.write(instructions_content)
        
        # Run explode command with verbose flag
        result = runner.invoke(app, ["explode", "instructions.md", "--verbose"])
        
        # Check command succeeds
        assert result.exit_code == 0
        assert "Created Cursor rules" in result.stdout