"""Test CLI integration and general functionality."""

import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner

from airules import app


def test_cli_help():
    """Test that main CLI shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI tool for managing LLM IDE prompts and rules" in result.stdout
    assert "explode" in result.stdout
    assert "implode" in result.stdout
    assert "download" in result.stdout


def test_cli_no_args():
    """Test that CLI with no arguments shows help."""
    runner = CliRunner()
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cli_invalid_command():
    """Test that CLI with invalid command shows error."""
    runner = CliRunner()
    result = runner.invoke(app, ["invalid-command"])
    assert result.exit_code == 2  # Typer returns 2 for unknown commands


def test_all_commands_accessible():
    """Test that all main commands are accessible."""
    runner = CliRunner()
    
    # Test explode command
    result = runner.invoke(app, ["explode", "--help"])
    assert result.exit_code == 0
    
    # Test implode command
    result = runner.invoke(app, ["implode", "--help"])
    assert result.exit_code == 0
    
    # Test download command
    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0


def test_implode_subcommands():
    """Test that implode subcommands are accessible."""
    runner = CliRunner()
    
    # Test implode cursor subcommand
    result = runner.invoke(app, ["implode", "cursor", "--help"])
    assert result.exit_code == 0
    
    # Test implode github subcommand
    result = runner.invoke(app, ["implode", "github", "--help"])
    assert result.exit_code == 0


def test_cli_completion():
    """Test that CLI supports completion."""
    runner = CliRunner()
    
    # Test show completion
    result = runner.invoke(app, ["--show-completion"])
    assert result.exit_code == 0
    
    # Test install completion help
    result = runner.invoke(app, ["--install-completion", "--help"])
    assert result.exit_code == 0