import tempfile
from pathlib import Path
from typer.testing import CliRunner
from llm_ide_rules import app

def test_integration_full_lifecycle(monkeypatch):
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Use pytest's monkeypatch to safely change and restore the working directory
        monkeypatch.chdir(temp_dir)
        temp_path = Path(temp_dir)

        # 1. Download
        download_result = runner.invoke(app, ["download", "--repo", "iloveitaly/llm-ide-prompts", "--target", str(temp_path)])
        assert download_result.exit_code == 0
        
        # Verify basic download & explode
        assert Path("instructions.md").exists()
        assert Path("commands.md").exists()
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path("AGENTS.md").exists()
        
        # Keep a copy of the original instructions
        original_instructions = Path("instructions.md").read_text()

        # 2. Safe Delete
        delete_result = runner.invoke(app, ["delete", "--target", str(temp_path), "--yes"])
        assert delete_result.exit_code == 0
        
        # Verify safe delete worked
        assert not Path(".cursor/rules/python.mdc").exists()
        assert not Path("AGENTS.md").exists()
        assert Path("instructions.md").exists()

        # 3. Explode
        # Explode doesn't take --target, it operates on CWD
        explode_result = runner.invoke(app, ["explode", "instructions.md"])
        if explode_result.exit_code != 0:
            print("EXPLODE FAILED:", explode_result.stdout)
            print("EXPLODE EXCEPTION:", explode_result.exception)
        assert explode_result.exit_code == 0
        
        # Verify explode recreated files
        assert Path(".cursor/rules/python.mdc").exists()
        assert Path("AGENTS.md").exists()

        # 4. Implode
        # Implode requires an agent subcommand, we will use 'cursor'
        implode_result = runner.invoke(app, ["implode", "cursor", "imploded.md"])
        if implode_result.exit_code != 0:
            print("IMPLODE FAILED:", implode_result.stdout)
            print("IMPLODE EXCEPTION:", implode_result.exception)
        assert implode_result.exit_code == 0
        assert Path("imploded.md").exists()
        
        imploded_content = Path("imploded.md").read_text()
        assert "## Python" in imploded_content

        # 5. Delete Everything
        delete_all_result = runner.invoke(app, ["delete", "--everything", "--target", str(temp_path), "--yes"])
        assert delete_all_result.exit_code == 0
        
        # Verify everything generated/downloaded is gone
        assert not Path(".cursor/rules").exists()
        assert not Path(".cursor/commands").exists()
        assert not Path(".github/instructions").exists()
        assert not Path("AGENTS.md").exists()
        assert not Path("CLAUDE.md").exists()

