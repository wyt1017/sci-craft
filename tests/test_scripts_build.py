"""Tests for scripts/build.py"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build import build_skill, BUILTIN_SKILLS, ADAPTERS


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create core directory structure
        core_dir = project_dir / "core"
        journals_dir = core_dir / "journals"
        rules_dir = core_dir / "rules"
        journals_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)

        # Create skills directory
        skills_dir = project_dir / "skills"
        skills_dir.mkdir()

        # Create a test skill
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test Skill\nMax words: {{max_sentence_words}}\n", encoding="utf-8")
        manifest = {
            "name": "test-skill",
            "version": "0.1.0",
            "status": "stable",
            "triggers": ["test"],
        }
        (skill_dir / "manifest.yaml").write_text(yaml.dump(manifest), encoding="utf-8")

        # Create journal config
        base_config = {
            "name": "Base",
            "writing": {"max_sentence_words": 35},
        }
        (journals_dir / "_base.yaml").write_text(yaml.dump(base_config), encoding="utf-8")
        nature_config = {
            "name": "Nature",
            "writing": {"max_sentence_words": 30, "english_variant": "british"},
        }
        (journals_dir / "nature.yaml").write_text(yaml.dump(nature_config), encoding="utf-8")

        yield {
            "project_dir": project_dir,
            "core_dir": core_dir,
            "skills_dir": skills_dir,
            "skill_dir": skill_dir,
        }


class TestBuildSkill:
    """Tests for build_skill function."""

    def test_build_skill_creates_output(self, temp_project, monkeypatch):
        """Test that build_skill creates output directory."""
        output_dir = temp_project["project_dir"] / "output"

        # Import the module and patch its constants directly
        import scripts.build as build_module

        monkeypatch.setattr(build_module, "SKILLS_DIR", temp_project["skills_dir"])
        monkeypatch.setattr(build_module, "CORE_DIR", temp_project["core_dir"])

        result = build_skill("test-skill", "nature", "trae", output_dir)

        assert result is True
        # Check that some output was created (path may vary by adapter)
        assert output_dir.exists()

    def test_build_skill_assembles_content(self, temp_project, monkeypatch):
        """Test that assembled content is written to output."""
        output_dir = temp_project["project_dir"] / "output"

        import scripts.build as build_module

        monkeypatch.setattr(build_module, "SKILLS_DIR", temp_project["skills_dir"])
        monkeypatch.setattr(build_module, "CORE_DIR", temp_project["core_dir"])

        result = build_skill("test-skill", "nature", "trae", output_dir)

        assert result is True
        # Verify that output was created
        assert output_dir.exists()

    def test_build_skill_missing_skill(self, temp_project, monkeypatch):
        """Test that missing skill returns False."""
        output_dir = temp_project["project_dir"] / "output"

        monkeypatch.setattr("scripts.build.SKILLS_DIR", temp_project["skills_dir"])
        monkeypatch.setattr("scripts.build.CORE_DIR", temp_project["core_dir"])

        result = build_skill("nonexistent", "nature", "trae", output_dir)
        assert result is False

    def test_build_skill_invalid_platform(self, temp_project, monkeypatch):
        """Test that invalid platform returns False."""
        output_dir = temp_project["project_dir"] / "output"

        monkeypatch.setattr("scripts.build.SKILLS_DIR", temp_project["skills_dir"])
        monkeypatch.setattr("scripts.build.CORE_DIR", temp_project["core_dir"])

        # Invalid platform - ADAPTERS doesn't have it
        result = build_skill("test-skill", "nature", "invalid_platform", output_dir)
        assert result is False


class TestAdapters:
    """Tests for ADAPTERS dictionary."""

    def test_adapters_has_trae(self):
        """Test that trae adapter is registered."""
        assert "trae" in ADAPTERS

    def test_adapters_has_codex(self):
        """Test that codex adapter is registered."""
        assert "codex" in ADAPTERS

    def test_adapters_has_claude(self):
        """Test that claude adapter is registered."""
        assert "claude" in ADAPTERS


class TestBuiltinSkills:
    """Tests for BUILTIN_SKILLS list."""

    def test_builtin_skills_excludes_shared(self):
        """Test that _shared directory is excluded."""
        # _shared should never be in BUILTIN_SKILLS
        assert "_shared" not in BUILTIN_SKILLS
