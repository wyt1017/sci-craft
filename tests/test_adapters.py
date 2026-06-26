"""Tests for adapters/"""
import tempfile
from pathlib import Path

import yaml

from adapters.trae import TraeAdapter


def _make_skill_dir(tmpdir: Path) -> Path:
    """Create a minimal skill directory for testing."""
    skill_dir = tmpdir / "sci-test"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n\nContent here.", encoding="utf-8")
    (skill_dir / "README.md").write_text("# Test Skill README", encoding="utf-8")
    (skill_dir / "manifest.yaml").write_text(
        yaml.dump({"name": "sci-test", "version": "0.1.0", "status": "stable", "triggers": ["test skill"]}),
        encoding="utf-8",
    )
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "guide.md").write_text("# Guide", encoding="utf-8")
    return skill_dir


def test_trae_adapter_copies_skill_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = TraeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert (output_dir / "sci-test" / "SKILL.md").exists()
        content = (output_dir / "sci-test" / "SKILL.md").read_text(encoding="utf-8")
        assert "# Test Skill" in content


def test_trae_adapter_copies_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = TraeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert (output_dir / "sci-test" / "manifest.yaml").exists()


def test_trae_adapter_copies_references():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = TraeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert (output_dir / "sci-test" / "references" / "guide.md").exists()


def test_trae_adapter_install_path():
    adapter = TraeAdapter()
    path = adapter.get_install_path()
    assert ".trae" in str(path) or "skills" in str(path)
