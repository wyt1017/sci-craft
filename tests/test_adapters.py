"""Tests for adapters/"""

import tempfile
from pathlib import Path

import yaml

from adapters.claude import ClaudeAdapter
from adapters.codex import CodexAdapter
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


def _make_skill_with_shared(tmpdir: Path) -> Path:
    """Create a skill directory with a _shared sibling.

    Directory structure mimics the real build flow after build.py copies _shared:
    tmpdir/
    └── output/
        └── _temp/
            ├── sci-test/       <- skill_dir (returned, copied from skills/sci-test)
            │   ├── SKILL.md
            │   └── manifest.yaml
            └── _shared/        <- copied by build.py for Claude adapter
                ├── glossary.md
                └── style.md
    """
    # Create the _temp output structure
    temp_dir = tmpdir / "output" / "_temp"
    temp_dir.mkdir(parents=True)
    skill_dir = temp_dir / "sci-test"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n\nContent here.", encoding="utf-8")
    (skill_dir / "manifest.yaml").write_text(
        yaml.dump({"name": "sci-test", "version": "0.1.0"}),
        encoding="utf-8",
    )

    # Create _shared alongside _temp/skill-name (as build.py does)
    shared_dir = temp_dir / "_shared"
    shared_dir.mkdir()
    (shared_dir / "glossary.md").write_text("# Glossary\n\nTerm definitions.", encoding="utf-8")
    (shared_dir / "style.md").write_text("# Style Guide\n\nWrite clearly.", encoding="utf-8")

    return skill_dir


# --- TRAE adapter tests ---


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


def test_trae_adapter_platform_name():
    adapter = TraeAdapter()
    assert adapter.platform_name == "trae"


def test_trae_adapter_overwrites_existing():
    """Test that adapter handles pre-existing destination gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = TraeAdapter()
        # First adaptation
        adapter.adapt_skill(skill_dir, output_dir)
        assert (output_dir / "sci-test" / "SKILL.md").exists()

        # Second adaptation (should overwrite without error)
        adapter.adapt_skill(skill_dir, output_dir)
        assert (output_dir / "sci-test" / "SKILL.md").exists()


# --- Codex adapter tests ---


def test_codex_adapter_copies_skill_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = CodexAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert (output_dir / "sci-test" / "SKILL.md").exists()
        content = (output_dir / "sci-test" / "SKILL.md").read_text(encoding="utf-8")
        assert "# Test Skill" in content


def test_codex_adapter_removes_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = CodexAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert not (output_dir / "sci-test" / "manifest.yaml").exists()


def test_codex_adapter_install_path():
    adapter = CodexAdapter()
    path = adapter.get_install_path()
    assert ".codex" in str(path)


def test_codex_adapter_build():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = CodexAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        dest = output_dir / "sci-test"
        assert dest.exists()
        assert (dest / "SKILL.md").exists()
        assert (dest / "README.md").exists()
        assert (dest / "references" / "guide.md").exists()
        assert not (dest / "manifest.yaml").exists()


def test_codex_adapter_platform_name():
    adapter = CodexAdapter()
    assert adapter.platform_name == "codex"


def test_codex_adapter_handles_missing_manifest():
    """Test that adapter works when manifest.yaml doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "sci-test"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = CodexAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert (output_dir / "sci-test" / "SKILL.md").exists()


# --- Claude adapter tests ---


def test_claude_adapter_renames_to_claude_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = ClaudeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert not (output_dir / "sci-test" / "SKILL.md").exists()
        assert (output_dir / "sci-test" / "CLAUDE.md").exists()
        content = (output_dir / "sci-test" / "CLAUDE.md").read_text(encoding="utf-8")
        assert "# Test Skill" in content


def test_claude_adapter_removes_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = ClaudeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        assert not (output_dir / "sci-test" / "manifest.yaml").exists()


def test_claude_adapter_install_path():
    adapter = ClaudeAdapter()
    path = adapter.get_install_path()
    assert path == Path.cwd()


def test_claude_adapter_inlines_shared():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_with_shared(Path(tmpdir))
        output_dir = Path(tmpdir) / "output" / "claude" / "nature"

        adapter = ClaudeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        claude_md = output_dir / "sci-test" / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text(encoding="utf-8")
        assert "# Shared Resources" in content
        assert "## glossary" in content
        assert "## style" in content
        assert "Term definitions." in content


def test_claude_adapter_platform_name():
    adapter = ClaudeAdapter()
    assert adapter.platform_name == "claude"


def test_claude_adapter_handles_no_shared():
    """Test that adapter works when _shared directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill_dir(Path(tmpdir))
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()

        adapter = ClaudeAdapter()
        adapter.adapt_skill(skill_dir, output_dir)

        # Should not raise an error
        claude_md = output_dir / "sci-test" / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text(encoding="utf-8")
        assert "# Shared Resources" not in content
