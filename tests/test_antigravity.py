"""Tests for Antigravity CLI agent integration."""

import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from llm_ide_rules import app
from llm_ide_rules.agents.antigravity import AntigravityAgent


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    lines = text.strip().split("\n")
    normalized_lines = [line.rstrip() for line in lines]
    while normalized_lines and not normalized_lines[-1]:
        normalized_lines.pop()
    return "\n".join(normalized_lines)


def extract_sections(text: str) -> dict[str, str]:
    """Extract sections from markdown text for easier comparison."""
    marker = "<!-- END CLONED INSTRUCTIONS -->"
    if marker in text:
        text = text.split(marker, 1)[0]

    sections = {}
    current_section = None
    current_content = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def test_antigravity_write_rule():
    """Test that AntigravityAgent writes rules with correct YAML frontmatter."""
    agent = AntigravityAgent()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        rules_dir = temp_path / ".agents/rules"

        # 1. Test standard rule with glob pattern
        agent.write_rule(
            content_lines=["## Python\n", "Python rules here.\n"],
            filename="python",
            rules_dir=rules_dir,
            glob_pattern="*.py",
            description="Python development rules",
        )

        rule_file = rules_dir / "python.md"
        assert rule_file.exists()
        content = rule_file.read_text()
        assert "description: Python development rules" in content
        assert 'globs: ["*.py"]' in content
        assert "alwaysApply: false" in content
        assert "Python rules here." in content

        # 2. Test manual rule
        agent.write_rule(
            content_lines=["## React\n", "React rules.\n"],
            filename="react",
            rules_dir=rules_dir,
            glob_pattern="manual",
            description="React frontend rules",
        )

        rule_file = rules_dir / "react.md"
        assert rule_file.exists()
        content = rule_file.read_text()
        assert "description: React frontend rules" in content
        assert "globs: []" in content
        assert "alwaysApply: false" in content

        # 3. Test general/always-apply rule
        agent.write_rule(
            content_lines=["General rules.\n"],
            filename="general",
            rules_dir=rules_dir,
            glob_pattern=None,
            description="General rules",
        )

        rule_file = rules_dir / "general.md"
        assert rule_file.exists()
        content = rule_file.read_text()
        assert "description: General rules" in content
        assert "globs: []" in content
        assert "alwaysApply: true" in content


def test_antigravity_write_command():
    """Test that AntigravityAgent writes commands/skills with correct format."""
    agent = AntigravityAgent()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        commands_dir = temp_path / ".agents/skills"

        agent.write_command(
            content_lines=[
                "## Deploy App\n",
                "Description: How to deploy\n",
                "\n",
                "Run fab deploy.\n",
            ],
            filename="deploy-app",
            commands_dir=commands_dir,
            section_name="Deploy App",
        )

        skill_file = commands_dir / "deploy-app/SKILL.md"
        assert skill_file.exists()
        content = skill_file.read_text()
        assert "name: deploy-app" in content
        assert "description: How to deploy" in content
        assert "# Deploy App" in content
        assert "Run fab deploy." in content


def test_roundtrip_antigravity_instructions():
    """Test explode -> implode antigravity produces equivalent instructions.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            original_content = """# Sample Instructions

## Python

globs: *.py
Description: Python rule description

Here are Python rules for development.

Use Python 3.13 and prefer Pathlib.

## React

globs: manual
Description: React rule description

Here are React rules for frontend development.

Use functional components and hooks.
"""

            Path("instructions.md").write_text(original_content)

            explode_result = runner.invoke(app, ["explode", "antigravity"])
            assert explode_result.exit_code == 0

            assert Path(".agents/rules/python.md").exists()
            assert Path(".agents/rules/react.md").exists()

            implode_result = runner.invoke(
                app, ["implode", "antigravity", "roundtrip.md"]
            )
            assert implode_result.exit_code == 0

            roundtrip_content = Path("roundtrip.md").read_text()

            original_sections = extract_sections(original_content)
            roundtrip_sections = extract_sections(roundtrip_content)

            assert set(original_sections.keys()) == set(roundtrip_sections.keys())

            for section_name in original_sections:
                assert normalize_whitespace(
                    original_sections[section_name]
                ) == normalize_whitespace(roundtrip_sections[section_name])
        finally:
            os.chdir(original_cwd)


def test_roundtrip_antigravity_commands():
    """Test explode -> implode antigravity produces equivalent commands.md."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            instructions_content = """# Sample Instructions

## Python

Python rules.
"""
            Path("instructions.md").write_text(instructions_content)

            commands_content = """## Fix Tests

Description: Fix failing tests

Run pytest and fix any errors that occur.

## Plan Only

Description: Plan without executing

Create a plan for the implementation.
"""
            Path("commands.md").write_text(commands_content)

            explode_result = runner.invoke(app, ["explode", "antigravity"])
            assert explode_result.exit_code == 0

            assert Path(".agents/skills/fix-tests/SKILL.md").exists()
            assert Path(".agents/skills/plan-only/SKILL.md").exists()

            implode_result = runner.invoke(app, ["implode", "antigravity"])
            assert implode_result.exit_code == 0

            roundtrip_content = Path("commands.md").read_text()

            original_sections = extract_sections(commands_content)
            roundtrip_sections = extract_sections(roundtrip_content)

            assert set(original_sections.keys()) == set(roundtrip_sections.keys())

            for section_name in original_sections:
                original_normalized = normalize_whitespace(
                    original_sections[section_name]
                )
                roundtrip_normalized = normalize_whitespace(
                    roundtrip_sections[section_name]
                )
                assert original_normalized == roundtrip_normalized
        finally:
            os.chdir(original_cwd)


def test_extract_frontmatter_description():
    """Test extracting single-line and multiline frontmatter descriptions."""
    from llm_ide_rules.agents.dotagents import extract_frontmatter_description

    # Single-line
    lines = ["---", "name: test-skill", "description: Simple description", "---"]
    assert extract_frontmatter_description(lines) == "Simple description"

    # Folded scalar >-
    lines_folded = [
        "---",
        "name: copier-sync",
        "description: >-",
        "  First line of description,",
        "  second line of description.",
        "---",
    ]
    assert (
        extract_frontmatter_description(lines_folded)
        == "First line of description, second line of description."
    )

    # Literal scalar |
    lines_literal = [
        "---",
        "name: multiline-skill",
        "description: |",
        "  Line 1",
        "  Line 2",
        "---",
    ]
    assert extract_frontmatter_description(lines_literal) == "Line 1\nLine 2"

    # Empty frontmatter
    assert extract_frontmatter_description([]) is None
    assert extract_frontmatter_description(["not frontmatter"]) is None


def test_get_ordered_files_skill_paths():
    """Test get_ordered_files correctly handles SKILL.md paths by using parent directory name."""
    from llm_ide_rules.agents.base import get_ordered_files

    skills = [
        Path(".agents/skills/zebra/SKILL.md"),
        Path(".agents/skills/apple/SKILL.md"),
        Path(".agents/skills/banana/SKILL.md"),
    ]

    # Alphabetical by parent directory name
    ordered = get_ordered_files(skills)
    assert [p.parent.name for p in ordered] == ["apple", "banana", "zebra"]

    # Explicit ordering via section_globs_keys
    custom_ordered = get_ordered_files(skills, ["Zebra", "Apple"])
    assert [p.parent.name for p in custom_ordered] == ["zebra", "apple", "banana"]


def test_bundle_rules_skips_title_description():
    """Test bundle_rules skips Description when it matches the title/name, but preserves distinct descriptions."""
    agent = AntigravityAgent()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        rules_dir = temp_path / ".agents/rules"
        rules_dir.mkdir(parents=True)

        # Rule whose description is just the name
        (rules_dir / "react.md").write_text(
            "---\ndescription: React\nglobs: []\nalwaysApply: true\n---\n\n## React\n\nReact instructions.\n"
        )
        # Rule with a distinct description
        (rules_dir / "python.md").write_text(
            "---\ndescription: Python coding style\nglobs: []\nalwaysApply: true\n---\n\n## Python\n\nPython instructions.\n"
        )

        output_file = temp_path / "instructions.md"
        agent.bundle_rules(output_file)

        bundled = output_file.read_text()
        assert "## React" in bundled
        assert "Description: React" not in bundled
        assert "## Python" in bundled
        assert "Description: Python coding style" in bundled
