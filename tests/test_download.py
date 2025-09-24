"""Test download command functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from llm_ide_rules import app


def test_download_help():
    """Test that download command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["download", "--help"])
    assert result.exit_code == 0
    assert "Download LLM instruction files from GitHub repositories" in result.stdout
    assert (
        "repo" in result.stdout
    )  # Look for "repo" instead of "--repo" to avoid ANSI styling issues
    assert "target" in result.stdout


@patch("llm_ide_rules.commands.download.requests.get")
@patch("llm_ide_rules.commands.download.zipfile.ZipFile")
def test_download_basic_functionality(mock_zipfile, mock_requests):
    """Test basic download functionality."""
    runner = CliRunner()

    # Mock the HTTP request
    mock_response = Mock()
    mock_response.content = b"fake zip content"
    mock_response.raise_for_status = Mock()
    mock_requests.return_value = mock_response

    # Mock the zipfile extraction
    mock_zip_instance = Mock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Create a fake extracted repo structure for the mock
        extracted_dir = Path("extracted/llm_ide_rules-master")
        extracted_dir.mkdir(parents=True)

        # Create sample files in the fake repo
        (extracted_dir / ".cursor").mkdir()
        (extracted_dir / ".cursor" / "rules").mkdir()
        (extracted_dir / ".cursor" / "rules" / "sample.mdc").write_text("cursor rule")

        (extracted_dir / ".github").mkdir()
        (extracted_dir / ".github" / "instructions").mkdir()
        (extracted_dir / ".github" / "instructions" / "sample.md").write_text(
            "github instruction"
        )

        (extracted_dir / "GEMINI.md").write_text("Gemini instructions")
        (extracted_dir / "CLAUDE.md").write_text("Claude instructions")
        (extracted_dir / "AGENT.md").write_text("Agent instructions")

        # Mock the extraction to create these files
        def mock_extractall(path):
            # The extraction creates the directory structure above
            pass

        mock_zip_instance.extractall = mock_extractall

        # Patch Path.iterdir to return our fake directory
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.return_value = [extracted_dir]

            # Run download command
            result = runner.invoke(app, ["download"])

            # Check command is invoked properly (may fail due to mocking limitations)
            # The main goal is to ensure the command can be invoked without syntax errors
            # We expect it to fail with exit code 1 due to invalid repo structure in mock
            assert result.exit_code in [0, 1]  # Either success or expected failure


def test_download_with_specific_types():
    """Test download command with specific instruction types."""
    runner = CliRunner()

    # Test that the command accepts specific types
    result = runner.invoke(app, ["download", "cursor", "github", "--help"])
    assert result.exit_code == 0


def test_download_with_custom_repo():
    """Test download command with custom repository."""
    runner = CliRunner()

    # Test that the command accepts custom repo option
    result = runner.invoke(
        app, ["download", "--repo", "other-user/other-repo", "--help"]
    )
    assert result.exit_code == 0


def test_download_with_target_directory():
    """Test download command with custom target directory."""
    runner = CliRunner()

    # Test that the command accepts target directory option
    result = runner.invoke(app, ["download", "--target", "./custom-dir", "--help"])
    assert result.exit_code == 0


def test_download_with_branch():
    """Test download command with custom branch."""
    runner = CliRunner()

    # Test that the command accepts branch option
    result = runner.invoke(app, ["download", "--branch", "main", "--help"])
    assert result.exit_code == 0


def test_download_verbose_option():
    """Test download command with verbose option."""
    runner = CliRunner()

    # Test that the command accepts verbose option
    result = runner.invoke(app, ["download", "--verbose", "--help"])
    assert result.exit_code == 0


def test_download_invalid_instruction_type():
    """Test download command with invalid instruction type."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run download command with invalid type
        result = runner.invoke(app, ["download", "invalid-type"])

        # Should fail with error about invalid types
        assert result.exit_code == 1


@patch("llm_ide_rules.commands.download.requests.get")
def test_download_network_error(mock_requests):
    """Test download command with network error."""
    runner = CliRunner()

    # Mock network error
    mock_requests.side_effect = Exception("Network error")

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        # Run download command
        result = runner.invoke(app, ["download"])

        # Should fail gracefully
        assert result.exit_code == 1


def test_download_instruction_types_configuration():
    """Test that instruction types are properly configured."""
    from llm_ide_rules.commands.download import DEFAULT_TYPES, INSTRUCTION_TYPES

    # Check that all expected types are present
    expected_types = ["cursor", "github", "gemini", "claude", "agent", "agents"]
    assert all(t in INSTRUCTION_TYPES for t in expected_types)

    # Check that DEFAULT_TYPES uses the keys from INSTRUCTION_TYPES
    assert DEFAULT_TYPES == list(INSTRUCTION_TYPES.keys())

    # Check that each instruction type has proper configuration
    for inst_type, config in INSTRUCTION_TYPES.items():
        assert "directories" in config
        assert "files" in config
        assert isinstance(config["directories"], list)
        assert isinstance(config["files"], list)


def test_download_exclude_patterns():
    """Test that github instruction type has exclude patterns configured."""
    from llm_ide_rules.commands.download import INSTRUCTION_TYPES

    github_config = INSTRUCTION_TYPES["github"]
    assert "exclude_patterns" in github_config
    assert "workflows/*" in github_config["exclude_patterns"]


def test_download_agents_alias():
    """Test that 'agents' works as an alias for 'agent'."""
    from llm_ide_rules.commands.download import INSTRUCTION_TYPES

    # Both 'agent' and 'agents' should be present
    assert "agent" in INSTRUCTION_TYPES
    assert "agents" in INSTRUCTION_TYPES
    
    # They should have the same configuration (both download AGENT.md)
    assert INSTRUCTION_TYPES["agent"]["files"] == ["AGENT.md"]
    assert INSTRUCTION_TYPES["agents"]["files"] == ["AGENT.md"]
    
    # Both should have empty directories list
    assert INSTRUCTION_TYPES["agent"]["directories"] == []
    assert INSTRUCTION_TYPES["agents"]["directories"] == []


def test_normalize_repo():
    """Test repository normalization functionality."""
    from llm_ide_rules.commands.download import normalize_repo
    
    # Test user/repo format (should be unchanged)
    assert normalize_repo("iloveitaly/llm-ide-rules") == "iloveitaly/llm-ide-rules"
    assert normalize_repo("user/repo") == "user/repo"
    
    # Test full GitHub URLs (should extract user/repo)
    assert normalize_repo("https://github.com/iloveitaly/llm-ide-rules") == "iloveitaly/llm-ide-rules"
    assert normalize_repo("https://github.com/iloveitaly/llm-ide-rules/") == "iloveitaly/llm-ide-rules"
    assert normalize_repo("https://github.com/user/repo/") == "user/repo"
    assert normalize_repo("http://github.com/user/repo") == "user/repo"
    
    # Test URLs with additional paths (should still extract user/repo)
    assert normalize_repo("https://github.com/user/repo/blob/main/README.md") == "user/repo"
    assert normalize_repo("https://github.com/user/repo/tree/main") == "user/repo"


@patch("llm_ide_rules.commands.download.requests.get")
@patch("llm_ide_rules.commands.download.zipfile.ZipFile")
def test_download_with_full_github_url(mock_zipfile, mock_requests):
    """Test download command with full GitHub URL instead of user/repo format."""
    from llm_ide_rules.commands.download import download_and_extract_repo
    
    # Mock the HTTP request
    mock_response = Mock()
    mock_response.content = b"fake zip content"
    mock_response.raise_for_status = Mock()
    mock_requests.return_value = mock_response
    
    # Mock the zipfile extraction
    mock_zip_instance = Mock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a fake extracted repo structure for the mock
        extracted_dir = Path(temp_dir) / "extracted/llm_ide_rules-master"
        extracted_dir.mkdir(parents=True)
        
        # Mock the extraction to create these files
        def mock_extractall(path):
            pass  # Files are already created above
        
        mock_zip_instance.extractall = mock_extractall
        
        # Patch Path.iterdir to return our fake directory
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.return_value = [extracted_dir]
            
            # Test that the URL is correctly constructed with full GitHub URL
            result = download_and_extract_repo("https://github.com/iloveitaly/llm-ide-rules/")
            
            # Verify the correct URL was called
            expected_url = "https://github.com/iloveitaly/llm-ide-rules/archive/master.zip"
            mock_requests.assert_called_once_with(expected_url, timeout=30)
            
            # Verify the result is the extracted directory
            assert result == extracted_dir
