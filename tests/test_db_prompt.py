"""Test the db_prompt command functionality."""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from airules import app


def test_db_prompt_command_exists():
    """Test that the db-prompt command exists in the CLI."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert "db-prompt" in result.stdout
    assert "Generate database schema prompts using llm-sql-prompt" in result.stdout


def test_db_prompt_help():
    """Test that the db-prompt command help works."""
    runner = CliRunner()
    result = runner.invoke(app, ["db-prompt", "--help"])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.stdout
    assert "exclude" in result.stdout  # Just check for key words due to ANSI formatting
    assert "stats" in result.stdout


def test_db_prompt_requires_database_url():
    """Test that db-prompt requires a database URL argument."""
    runner = CliRunner()
    result = runner.invoke(app, ["db-prompt"])
    assert result.exit_code == 2
    # Check that the error message is in stderr or stdout
    output = result.stdout + result.stderr
    assert "Missing argument" in output or "DATABASE_URL" in output


@patch('llm_sql_prompt.postgres')
def test_db_prompt_stats_filtering(mock_postgres):
    """Test that stats tables are filtered when exclude_stats is True."""
    runner = CliRunner()
    
    # Mock the postgres module function
    mock_postgres.describe_database_and_table = MagicMock()
    
    # Test with explicit stats table names - should be filtered out
    result = runner.invoke(app, [
        "db-prompt", 
        "postgresql://test:test@localhost/test",
        "--table", "users",
        "--table", "pg_stat_statements", 
        "--table", "products",
        "--exclude-stats"
    ])
    
    # Should call with filtered table list (no stats tables)
    mock_postgres.describe_database_and_table.assert_called_once()
    args = mock_postgres.describe_database_and_table.call_args[0]
    assert "users" in args[1]
    assert "products" in args[1] 
    assert "pg_stat_statements" not in args[1]


@patch('llm_sql_prompt.postgres')
def test_db_prompt_include_stats_option(mock_postgres):
    """Test that stats tables are included when --include-stats is used."""
    runner = CliRunner()
    
    # Mock the postgres module function
    mock_postgres.describe_database_and_table = MagicMock()
    
    # Test with --include-stats - should NOT filter stats tables
    result = runner.invoke(app, [
        "db-prompt", 
        "postgresql://test:test@localhost/test",
        "--table", "users",
        "--table", "pg_stat_statements", 
        "--include-stats"
    ])
    
    # Should call with unfiltered table list (including stats tables)
    mock_postgres.describe_database_and_table.assert_called_once()
    args = mock_postgres.describe_database_and_table.call_args[0]
    assert "users" in args[1]
    assert "pg_stat_statements" in args[1]


@patch('llm_sql_prompt.postgres')
def test_db_prompt_handles_postgres_error(mock_postgres):
    """Test that pg_stat_statements errors are handled gracefully."""
    runner = CliRunner()
    
    # Mock the postgres module to raise the specific error
    mock_postgres.describe_database_and_table.side_effect = Exception(
        'pg_stat_statements must be loaded via "shared_preload_libraries"'
    )
    
    result = runner.invoke(app, [
        "db-prompt", 
        "postgresql://test:test@localhost/test",
        "--all"
    ])
    
    assert result.exit_code == 1
    assert "PostgreSQL statistics tables require special configuration" in result.stdout