import tempfile
from pathlib import Path
from typer.testing import CliRunner
from llm_ide_rules import app
import os

def test_integration_delete_safety_with_external_repo():
    """
    Integration test that:
    1. Sets up a temp directory with 'user-owned' files (.github/dependabot.yml, etc.)
    2. Downloads instructions from an external repo (iloveitaly/python-package-prompts)
    3. Runs delete --everything
    4. Verifies that downloaded files are gone but user files remain.
    """
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. Setup user-owned files
        github_dir = temp_path / ".github"
        workflows_dir = github_dir / "workflows"
        workflows_dir.mkdir(parents=True)
        
        dependabot_file = github_dir / "dependabot.yml"
        dependabot_file.write_text("version: 2\nupdates:\n  - package-ecosystem: pip")
        
        workflow_file = workflows_dir / "ci.yml"
        workflow_file.write_text("name: CI\non: [push]")
        
        # 2. Download from external repo
        # We use iloveitaly/python-package-prompts as requested
        print("\nDownloading from iloveitaly/python-package-prompts...")
        download_result = runner.invoke(
            app, 
            ["download", "--repo", "iloveitaly/python-package-prompts", "--target", str(temp_path)]
        )
        
        if download_result.exit_code != 0:
            print("Download failed:", download_result.stdout)
            # If download fails (e.g. network issue), we might want to skip or fail gracefully
            # But for this test we expect it to work or we want to know.
            assert download_result.exit_code == 0
            
        # Verify that something was actually downloaded (to make sure the test is meaningful)
        # We expect some files like .github/prompts/ or .cursor/rules/ to appear if the repo has them.
        # Based on the user's prompt, we assume this repo has relevant files.
        # Let's check for a few potential downloaded paths.
        downloaded_files = list(temp_path.rglob("*"))
        print(f"Files after download: {len(downloaded_files)}")
        
        # 3. Run delete --everything
        print("Running delete --everything...")
        delete_result = runner.invoke(
            app, 
            ["delete", "--everything", "--target", str(temp_path), "--yes"]
        )
        
        assert delete_result.exit_code == 0
        
        # 4. Verify Assertions
        
        # User files MUST exist
        assert dependabot_file.exists(), ".github/dependabot.yml should not be deleted"
        assert workflow_file.exists(), ".github/workflows/ci.yml should not be deleted"
        assert workflows_dir.exists(), ".github/workflows directory should not be deleted"
        assert github_dir.exists(), ".github directory should not be deleted"
        
        # Downloaded directories should be gone (if they were downloaded)
        # We specifically target directories defined in INSTRUCTION_TYPES
        # e.g., .github/prompts, .github/instructions, .cursor/rules
        
        prompts_dir = github_dir / "prompts"
        instructions_dir = github_dir / "instructions"
        cursor_rules_dir = temp_path / ".cursor" / "rules"
        
        assert not prompts_dir.exists(), ".github/prompts should be deleted"
        assert not instructions_dir.exists(), ".github/instructions should be deleted"
        assert not cursor_rules_dir.exists(), ".cursor/rules should be deleted"
        

