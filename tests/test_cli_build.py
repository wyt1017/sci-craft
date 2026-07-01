"""Tests for cli/build.py"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.build import find_project_root, build_single_skill, build_all_skills


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_find_project_root_from_project_dir(self):
        """Test finding root when in project directory."""
        # When called from project root, should find it
        root = find_project_root()
        # Should find a directory with skills and core
        assert (root / "skills").exists() or root == Path.cwd()

    def test_find_project_root_returns_cwd_if_not_found(self, monkeypatch):
        """Test that find_project_root returns cwd if no markers found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory without markers
            test_dir = Path(tmpdir) / "no_project"
            test_dir.mkdir()

            # Monkeypatch cwd to return our test directory
            monkeypatch.setattr("cli.build.Path.cwd", lambda: test_dir)

            result = find_project_root()
            assert result == test_dir


class TestBuildSingleSkill:
    """Tests for build_single_skill function."""

    @pytest.fixture
    def temp_build_project(self):
        """Create a temporary project for build testing."""
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
            (skill_dir / "SKILL.md").write_text(
                "# Test Skill\nMax: {{max_sentence_words}}\n",
                encoding="utf-8",
            )
            manifest = {
                "id": "test-skill",
                "name": "Test Skill",
                "version": "1.0.0",
                "status": "active",
                "triggers": ["test"],
            }
            (skill_dir / "manifest.yaml").write_text(yaml.dump(manifest), encoding="utf-8")

            # Create journal config
            base_config = {"name": "Base", "writing": {"max_sentence_words": 35}}
            (journals_dir / "_base.yaml").write_text(yaml.dump(base_config), encoding="utf-8")
            nature_config = {
                "name": "Nature",
                "writing": {"max_sentence_words": 30},
            }
            (journals_dir / "nature.yaml").write_text(yaml.dump(nature_config), encoding="utf-8")

            yield {
                "project_dir": project_dir,
                "core_dir": core_dir,
                "skills_dir": skills_dir,
                "skill_dir": skill_dir,
                "output_dir": project_dir / "build",
            }

    def test_build_single_skill_success(self, temp_build_project):
        """Test successful skill build."""
        output_dir = temp_build_project["output_dir"]

        result = build_single_skill(
            skill_name="test-skill",
            journal="nature",
            project_dir=temp_build_project["project_dir"],
            output_dir=output_dir,
            force=True,
        )

        assert result is True
        assert (output_dir / "nature" / "test-skill" / "SKILL.md").exists()

    def test_build_single_skill_missing_skill(self, temp_build_project):
        """Test build with missing skill."""
        output_dir = temp_build_project["output_dir"]

        result = build_single_skill(
            skill_name="nonexistent",
            journal="nature",
            project_dir=temp_build_project["project_dir"],
            output_dir=output_dir,
            force=True,
        )

        assert result is False

    def test_build_single_skill_renders_content(self, temp_build_project):
        """Test that skill content is created."""
        output_dir = temp_build_project["output_dir"]

        build_single_skill(
            skill_name="test-skill",
            journal="nature",
            project_dir=temp_build_project["project_dir"],
            output_dir=output_dir,
            force=True,
        )

        skill_md = output_dir / "nature" / "test-skill" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        # Template should be created (basic content check)
        assert "Test Skill" in content


class TestBuildAllSkills:
    """Tests for build_all_skills function."""

    @pytest.fixture
    def temp_multi_skill_project(self):
        """Create a temporary project with multiple skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create core directory structure
            core_dir = project_dir / "core"
            journals_dir = core_dir / "journals"
            journals_dir.mkdir(parents=True)

            # Create skills directory with multiple skills
            skills_dir = project_dir / "skills"
            skills_dir.mkdir()

            for i in range(3):
                skill_dir = skills_dir / f"skill-{i}"
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"# Skill {i}\n", encoding="utf-8")
                manifest = {
                    "id": f"skill-{i}",
                    "name": f"Skill {i}",
                    "version": "1.0.0",
                    "status": "active",
                    "triggers": ["test"],
                }
                (skill_dir / "manifest.yaml").write_text(yaml.dump(manifest), encoding="utf-8")

            # Create journal config
            base_config = {"name": "Base"}
            (journals_dir / "_base.yaml").write_text(yaml.dump(base_config), encoding="utf-8")
            nature_config = {"name": "Nature"}
            (journals_dir / "nature.yaml").write_text(yaml.dump(nature_config), encoding="utf-8")

            yield {
                "project_dir": project_dir,
                "skills_dir": skills_dir,
                "output_dir": project_dir / "build",
            }

    def test_build_all_skills_count(self, temp_multi_skill_project):
        """Test that all skills are built."""
        output_dir = temp_multi_skill_project["output_dir"]

        count = build_all_skills(
            journal="nature",
            project_dir=temp_multi_skill_project["project_dir"],
            output_dir=output_dir,
            incremental=False,
        )

        assert count == 3

    def test_build_all_skills_creates_outputs(self, temp_multi_skill_project):
        """Test that outputs are created for all skills."""
        output_dir = temp_multi_skill_project["output_dir"]

        build_all_skills(
            journal="nature",
            project_dir=temp_multi_skill_project["project_dir"],
            output_dir=output_dir,
            incremental=False,
        )

        for i in range(3):
            assert (output_dir / "nature" / f"skill-{i}" / "SKILL.md").exists()
