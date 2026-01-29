import tempfile
from pathlib import Path

import click
from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.commands.delete import find_files_to_delete


def test_delete_help():
    """Test that delete command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["delete", "--help"])
    assert result.exit_code == 0
    stdout = click.unstyle(result.stdout)
    assert "Remove downloaded LLM instruction files" in stdout
    assert "--yes" in stdout
    assert "--target" in stdout


def test_find_files_to_delete_cursor():
    """Test finding Cursor files to delete."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_dir = temp_path / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.mdc").write_text("test")

        dirs, files = find_files_to_delete(["cursor"], temp_path)

        assert len(dirs) == 1
        assert dirs[0] == rules_dir
        assert len(files) == 0


def test_find_files_to_delete_gemini():
    """Test finding Gemini files to delete."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        gemini_dir = temp_path / ".gemini"
        commands_dir = gemini_dir / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "test.toml").write_text("test")

        gemini_file = temp_path / "GEMINI.md"
        gemini_file.write_text("test")

        dirs, files = find_files_to_delete(["gemini"], temp_path)

        assert len(dirs) == 1
        assert dirs[0] == commands_dir
        assert len(files) == 0
        # GEMINI.md is no longer managed by gemini agent
        assert gemini_file not in files


def test_find_files_to_delete_agents():
    """Test finding AGENTS.md file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        (temp_path / "AGENTS.md").write_text("root")

        dirs, files = find_files_to_delete(["agents"], temp_path)

        assert len(dirs) == 0
        assert len(files) == 1
        assert files[0] == temp_path / "AGENTS.md"


def test_find_files_to_delete_nonexistent():
    """Test finding files when nothing exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        dirs, files = find_files_to_delete(["cursor", "github"], temp_path)

        assert len(dirs) == 0
        assert len(files) == 0


def test_find_files_to_delete_unknown_type():
    """Test unknown instruction type warning."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        dirs, files = find_files_to_delete(["unknown_type"], temp_path)

        assert len(dirs) == 0
        assert len(files) == 0


def test_delete_with_yes_flag():
    """Test delete with --yes flag skips confirmation."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_dir = temp_path / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "test.mdc").write_text("test")

        result = runner.invoke(
            app, ["delete", "cursor", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0
        assert "Successfully deleted" in result.stdout
        assert not rules_dir.exists()


def test_delete_with_confirmation_yes():
    """Test delete with confirmation accepted."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_dir = temp_path / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True)

        result = runner.invoke(
            app, ["delete", "cursor", "--target", temp_dir, "--everything"], input="y\n"
        )

        assert result.exit_code == 0
        assert "Successfully deleted" in result.stdout
        assert not rules_dir.exists()


def test_delete_with_confirmation_no():
    """Test delete with confirmation rejected."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_dir = temp_path / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True)

        result = runner.invoke(
            app, ["delete", "cursor", "--target", temp_dir, "--everything"], input="n\n"
        )

        assert result.exit_code == 0
        assert "Deletion cancelled" in result.stdout
        assert rules_dir.exists()


def test_delete_invalid_instruction_type():
    """Test delete with invalid instruction type."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["delete", "invalid_type", "--target", temp_dir])

        assert result.exit_code == 1


def test_delete_nonexistent_target_dir():
    """Test delete with nonexistent target directory."""
    runner = CliRunner()

    result = runner.invoke(app, ["delete", "--target", "/nonexistent/path"])

    assert result.exit_code == 1
    assert "does not exist" in result.stdout


def test_delete_no_matching_files():
    """Test delete when no matching files found."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["delete", "cursor", "--target", temp_dir, "--yes"])

        assert result.exit_code == 0
        assert "No matching instruction files found" in result.stdout


def test_delete_default_types():
    """Test delete without specifying types deletes all default types."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        (temp_path / ".cursor" / "rules").mkdir(parents=True)
        (temp_path / ".github" / "instructions").mkdir(parents=True)
        (temp_path / ".github" / "prompts").mkdir(parents=True)
        (temp_path / "GEMINI.md").write_text("test")
        (temp_path / "CLAUDE.md").write_text("test")
        (temp_path / "AGENTS.md").write_text("test")

        result = runner.invoke(app, ["delete", "--target", temp_dir, "--yes", "--everything"])

        assert result.exit_code == 0
        assert "Successfully deleted" in result.stdout
        assert not (temp_path / ".cursor" / "rules").exists()
        assert not (temp_path / ".github" / "instructions").exists()
        assert not (temp_path / ".github" / "prompts").exists()
        assert (temp_path / "GEMINI.md").exists()
        assert not (temp_path / "CLAUDE.md").exists()
        assert not (temp_path / "AGENTS.md").exists()


def test_delete_multiple_types():
    """Test delete with multiple specific types."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        (temp_path / ".cursor" / "rules").mkdir(parents=True)
        (temp_path / "GEMINI.md").write_text("test")
        (temp_path / "CLAUDE.md").write_text("test")

        result = runner.invoke(
            app, ["delete", "cursor", "gemini", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0
        assert not (temp_path / ".cursor" / "rules").exists()
        assert (temp_path / "GEMINI.md").exists()
        assert (temp_path / "CLAUDE.md").exists()


def test_delete_directory_with_subdirectories():
    """Test delete removes directories with subdirectories."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_dir = temp_path / ".cursor"
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "python.mdc").write_text("test")
        (rules_dir / "react.mdc").write_text("test")

        result = runner.invoke(app, ["delete", "cursor", "--target", temp_dir, "--yes", "--everything"])

        assert result.exit_code == 0
        assert not rules_dir.exists()