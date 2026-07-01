"""Tests for scripts/install.py"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.install import install, ADAPTERS


@pytest.fixture
def temp_install_setup():
    """Create a temporary project structure for install testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create output directory with built skills
        output_dir = project_dir / "output"
        platform_dir = output_dir / "trae" / "nature"
        platform_dir.mkdir(parents=True)

        # Create a test skill in output
        skill_output = platform_dir / "test-skill"
        skill_output.mkdir()
        (skill_output / "SKILL.md").write_text("# Test Skill\n", encoding="utf-8")

        # Create _shared in skills directory
        skills_dir = project_dir / "skills"
        skills_dir.mkdir()
        shared_dir = skills_dir / "_shared"
        shared_dir.mkdir()
        (shared_dir / "glossary.md").write_text("# Glossary\n", encoding="utf-8")

        yield {
            "project_dir": project_dir,
            "output_dir": output_dir,
            "platform_dir": platform_dir,
            "skill_output": skill_output,
            "skills_dir": skills_dir,
        }


class TestInstall:
    """Tests for install function."""

    def test_install_creates_destination(self, temp_install_setup, monkeypatch):
        """Test that install creates destination directory."""
        monkeypatch.setattr("scripts.install.PROJECT_ROOT", temp_install_setup["project_dir"])
        monkeypatch.setattr("scripts.install.OUTPUT_DIR", temp_install_setup["output_dir"])

        result = install("nature", "trae")

        assert result is True
        # Check that skill was installed
        install_path = Path.home() / ".trae" / "skills" / "test-skill"
        assert install_path.exists()

    def test_install_missing_output_returns_false(self, monkeypatch):
        """Test that install returns False if output doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            output_dir = project_dir / "output"

            monkeypatch.setattr("scripts.install.PROJECT_ROOT", project_dir)
            monkeypatch.setattr("scripts.install.OUTPUT_DIR", output_dir)

            result = install("nature", "trae")
            assert result is False

    def test_install_unknown_platform_returns_false(self, temp_install_setup, monkeypatch):
        """Test that install returns False for unknown platform."""
        monkeypatch.setattr("scripts.install.PROJECT_ROOT", temp_install_setup["project_dir"])
        monkeypatch.setattr("scripts.install.OUTPUT_DIR", temp_install_setup["output_dir"])

        result = install("nature", "unknown_platform")
        assert result is False

    def test_install_specific_skill(self, temp_install_setup, monkeypatch):
        """Test installing a specific skill."""
        monkeypatch.setattr("scripts.install.PROJECT_ROOT", temp_install_setup["project_dir"])
        monkeypatch.setattr("scripts.install.OUTPUT_DIR", temp_install_setup["output_dir"])

        result = install("nature", "trae", skill="test-skill")
        assert result is True

    def test_install_missing_skill_returns_false(self, temp_install_setup, monkeypatch):
        """Test that install returns False for missing skill."""
        monkeypatch.setattr("scripts.install.PROJECT_ROOT", temp_install_setup["project_dir"])
        monkeypatch.setattr("scripts.install.OUTPUT_DIR", temp_install_setup["output_dir"])

        result = install("nature", "trae", skill="nonexistent")
        assert result is False

    def test_install_force_overwrites(self, temp_install_setup, monkeypatch):
        """Test that force=True overwrites existing installation."""
        monkeypatch.setattr("scripts.install.PROJECT_ROOT", temp_install_setup["project_dir"])
        monkeypatch.setattr("scripts.install.OUTPUT_DIR", temp_install_setup["output_dir"])

        # First install
        install("nature", "trae")

        # Modify the installed skill
        install_path = Path.home() / ".trae" / "skills" / "test-skill" / "SKILL.md"
        original_content = install_path.read_text(encoding="utf-8")
        install_path.write_text("Modified content\n", encoding="utf-8")

        # Force reinstall
        install("nature", "trae", force=True)

        # Content should be restored
        new_content = install_path.read_text(encoding="utf-8")
        assert new_content == original_content


class TestInstallAdapters:
    """Tests for ADAPTERS dictionary in install module."""

    def test_adapters_has_trae(self):
        """Test that trae adapter is registered."""
        assert "trae" in ADAPTERS

    def test_adapters_has_codex(self):
        """Test that codex adapter is registered."""
        assert "codex" in ADAPTERS

    def test_adapters_has_claude(self):
        """Test that claude adapter is registered."""
        assert "claude" in ADAPTERS
