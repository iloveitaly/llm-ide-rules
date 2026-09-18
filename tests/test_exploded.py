"""Test exploded subcommand."""

from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app


def test_exploded_empty_directory(tmp_path: Path):
    "test exploded command outputs nothing when no agents are detected"
    runner = CliRunner()
    result = runner.invoke(app, ["exploded", "--target", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == ""


def test_exploded_single_client(tmp_path: Path):
    "test exploded command outputs single client when detected"
    runner = CliRunner()
    (tmp_path / ".cursor").mkdir()

    result = runner.invoke(app, ["exploded", "--target", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == "cursor\n"


def test_exploded_multiple_clients(tmp_path: Path):
    "test exploded command outputs each detected client on a new line"
    runner = CliRunner()
    (tmp_path / ".cursor").mkdir()
    (tmp_path / "CLAUDE.md").touch()
    (tmp_path / ".agents").mkdir()

    result = runner.invoke(app, ["exploded", "--target", str(tmp_path)])

    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert lines == ["cursor", "claude", "antigravity"]


def test_exploded_codex_client(tmp_path: Path):
    runner = CliRunner()
    (tmp_path / ".codex").mkdir()

    result = runner.invoke(app, ["exploded", "--target", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == "codex\n"


def test_exploded_target_argument(tmp_path: Path):
    "test exploded command accepts target directory as positional argument"
    runner = CliRunner()
    (tmp_path / ".cursor").mkdir()

    result = runner.invoke(app, ["exploded", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == "cursor\n"


def test_exploded_target_short_option(tmp_path: Path):
    "test exploded command accepts -t option"
    runner = CliRunner()
    (tmp_path / "CLAUDE.md").touch()

    result = runner.invoke(app, ["exploded", "-t", str(tmp_path)])

    assert result.exit_code == 0
    assert result.stdout == "claude\n"


def test_exploded_nonexistent_directory(tmp_path: Path):
    "test exploded command exits with error on nonexistent directory"
    runner = CliRunner()
    nonexistent = tmp_path / "nonexistent"

    result = runner.invoke(app, ["exploded", "--target", str(nonexistent)])

    assert result.exit_code == 1
    assert "does not exist" in result.stderr
