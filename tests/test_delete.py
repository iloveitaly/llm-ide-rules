import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.commands.delete import find_files_to_delete


def test_delete_help():
    """Test that delete command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["delete", "--help"])
    assert result.exit_code == 0
    assert "Remove downloaded LLM instruction files" in result.stdout
    assert "yes" in result.stdout
    assert "target" in result.stdout


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


def test_delete_comma_separated_types():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        cursor_rules = temp_path / ".cursor" / "rules"
        cursor_rules.mkdir(parents=True)
        (cursor_rules / "test.mdc").write_text("test")

        claude_rules = temp_path / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        (claude_rules / "test.md").write_text("test")

        github_instructions = temp_path / ".github" / "instructions"
        github_instructions.mkdir(parents=True)
        (github_instructions / "test.instructions.md").write_text("test")

        result = runner.invoke(
            app,
            ["delete", "cursor,claude", "--target", temp_dir, "--yes", "--everything"],
        )

        assert result.exit_code == 0
        assert not cursor_rules.exists()
        assert not claude_rules.exists()
        assert github_instructions.exists()


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
        (temp_path / ".claude" / "rules").mkdir(parents=True)
        (temp_path / "AGENTS.md").write_text("test")

        result = runner.invoke(
            app, ["delete", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0
        assert "Successfully deleted" in result.stdout
        assert not (temp_path / ".cursor" / "rules").exists()
        assert not (temp_path / ".github" / "instructions").exists()
        assert not (temp_path / ".github" / "prompts").exists()
        assert not (temp_path / ".claude" / "rules").exists()
        assert not (temp_path / "AGENTS.md").exists()


def test_delete_multiple_types():
    """Test delete with multiple specific types."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        (temp_path / ".cursor" / "rules").mkdir(parents=True)
        (temp_path / ".claude" / "rules").mkdir(parents=True)
        (temp_path / ".github" / "instructions").mkdir(parents=True)

        result = runner.invoke(
            app,
            [
                "delete",
                "cursor",
                "claude",
                "--target",
                temp_dir,
                "--yes",
                "--everything",
            ],
        )

        assert result.exit_code == 0
        assert not (temp_path / ".cursor" / "rules").exists()
        assert not (temp_path / ".claude" / "rules").exists()
        assert (temp_path / ".github" / "instructions").exists()


def test_find_files_to_delete_claude():
    """Test finding Claude files to delete."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        claude_rules_dir = temp_path / ".claude" / "rules"
        claude_rules_dir.mkdir(parents=True)
        (claude_rules_dir / "test.md").write_text("test")

        claude_commands_dir = temp_path / ".claude" / "commands"
        claude_commands_dir.mkdir(parents=True)
        (claude_commands_dir / "fix-tests.md").write_text("test")

        dirs, files = find_files_to_delete(["claude"], temp_path)

        assert len(dirs) == 2
        assert claude_rules_dir in dirs
        assert claude_commands_dir in dirs
        assert len(files) == 0


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

        result = runner.invoke(
            app, ["delete", "cursor", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0
        assert not rules_dir.exists()


def test_find_files_to_delete_ignores_node_modules_and_venv():
    """Test finding files to delete ignores node_modules and .venv directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "AGENTS.md").write_text("root")

        node_modules_dir = temp_path / "node_modules" / "some-package"
        node_modules_dir.mkdir(parents=True)
        (node_modules_dir / "AGENTS.md").write_text("package agents")

        nested_node_modules = temp_path / "web" / "node_modules" / "pkg"
        nested_node_modules.mkdir(parents=True)
        (nested_node_modules / "AGENTS.md").write_text("nested pkg agents")

        venv_dir = temp_path / ".venv" / "lib" / "python"
        venv_dir.mkdir(parents=True)
        (venv_dir / "AGENTS.md").write_text("venv agents")

        valid_subdir = temp_path / "packages" / "frontend"
        valid_subdir.mkdir(parents=True)
        (valid_subdir / "AGENTS.md").write_text("frontend agents")

        dirs, files = find_files_to_delete(["agents"], temp_path)

        assert len(dirs) == 0
        assert temp_path / "AGENTS.md" in files
        assert valid_subdir / "AGENTS.md" in files
        assert (node_modules_dir / "AGENTS.md") not in files
        assert (nested_node_modules / "AGENTS.md") not in files
        assert (venv_dir / "AGENTS.md") not in files


def test_delete_everything_ignores_node_modules_and_venv():
    """Test delete --everything does not delete files in node_modules or .venv."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "AGENTS.md").write_text("root")

        node_modules_agents = temp_path / "node_modules" / "pkg" / "AGENTS.md"
        node_modules_agents.parent.mkdir(parents=True)
        node_modules_agents.write_text("pkg")

        venv_agents = temp_path / ".venv" / "lib" / "AGENTS.md"
        venv_agents.parent.mkdir(parents=True)
        venv_agents.write_text("venv")

        result = runner.invoke(
            app, ["delete", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0
        assert not (temp_path / "AGENTS.md").exists()
        assert node_modules_agents.exists()
        assert venv_agents.exists()


def test_delete_default_ignores_node_modules_and_venv():
    """Test safe delete does not inspect or report node_modules or .venv files."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "instructions.md").write_text(
            "# Project Instructions\n\nGeneral instructions\n"
        )
        (temp_path / "AGENTS.md").write_text("General instructions")

        node_modules_agents = temp_path / "node_modules" / "pkg" / "AGENTS.md"
        node_modules_agents.parent.mkdir(parents=True)
        node_modules_agents.write_text("pkg")

        venv_agents = temp_path / ".venv" / "lib" / "AGENTS.md"
        venv_agents.parent.mkdir(parents=True)
        venv_agents.write_text("venv")

        result = runner.invoke(app, ["delete", "--target", temp_dir, "--yes"])

        assert result.exit_code == 0
        assert not (temp_path / "AGENTS.md").exists()
        assert node_modules_agents.exists()
        assert venv_agents.exists()
        assert "were skipped because they don't match" not in result.stdout
