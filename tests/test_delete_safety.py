import tempfile
from pathlib import Path
from typer.testing import CliRunner
from llm_ide_rules import app


def test_delete_everything_preserves_unmanaged_github_files():
    """Test that delete --everything does not delete unmanaged files in .github."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Setup .github directory
        github_dir = temp_path / ".github"
        github_dir.mkdir()

        # Create a "user-owned" file that should be preserved
        user_workflow = github_dir / "my-workflow.yml"
        user_workflow.write_text("name: My Workflow")

        # Create a "tool-owned" directory/file that should be deleted
        instructions_dir = github_dir / "instructions"
        instructions_dir.mkdir()
        (instructions_dir / "test.instructions.md").write_text("test")

        # Run delete --everything
        result = runner.invoke(
            app, ["delete", "--target", temp_dir, "--yes", "--everything"]
        )

        assert result.exit_code == 0

        # Check that user file still exists
        # This assertion is expected to FAIL until the fix is implemented
        assert user_workflow.exists(), "User file in .github was deleted!"

        # Check that tool file is deleted (this might fail if we change logic to be specific and only target existing tool dirs)
        # But for now, with the bug, everything is deleted.
        assert not instructions_dir.exists()
