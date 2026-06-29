"""Tests for builder/assembler.py"""
import tempfile
from pathlib import Path

from builder.assembler import Assembler, _deep_merge, _flatten, load_journal_config


def test_load_journal_config_nature():
    config = load_journal_config("nature", Path("core/journals"))
    assert config["name"] == "Nature"
    assert config["writing"]["max_sentence_words"] == 30
    assert config["writing"]["english_variant"] == "british"


def test_load_journal_config_science():
    config = load_journal_config("science", Path("core/journals"))
    assert config["name"] == "Science"
    assert config["writing"]["english_variant"] == "american"
    assert config["figure"]["min_dpi"] == 600


def test_load_journal_config_inherits_base():
    config = load_journal_config("nature", Path("core/journals"))
    # Should have base defaults for keys not overridden
    assert "submission" in config


def test_assembler_renders_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal skill template
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "# Test Skill\nMax words: {{max_sentence_words}}\nVariant: {{english_variant}}\n"
        )

        assembler = Assembler(Path("core"))
        result = assembler.assemble("nature", skill_dir)
        assert "Max words: 30" in result
        assert "Variant: british" in result


def test_assembler_renders_science():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "# Test\n{{max_sentence_words}} {{english_variant}}\n"
        )

        assembler = Assembler(Path("core"))
        result = assembler.assemble("science", skill_dir)
        assert "25 american" in result


def test_assembler_injects_rules():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "# Test\n{{RULES_INJECTION_POINT}}\n"
        )
        (skill_dir / "manifest.yaml").write_text(
            "rules:\n  - writing/sentence-length\n"
        )

        assembler = Assembler(Path("core"))
        result = assembler.assemble("nature", skill_dir)
        # Should contain the sentence-length rule content (rendered with journal params)
        assert "30" in result  # max_sentence_words for Nature


def test_deep_merge_does_not_mutate_base():
    """Test that _deep_merge returns a new dict without mutating base."""
    base = {"a": {"b": 1, "c": 2}}
    override = {"a": {"b": 3}}
    result = _deep_merge(base, override)

    assert result["a"]["b"] == 3
    assert base["a"]["b"] == 1  # Original should be unchanged


def test_flatten_produces_short_keys():
    """Test that _flatten produces both full-path and short leaf keys."""
    d = {"writing": {"max_sentence_words": 30, "english_variant": "british"}}
    flat = _flatten(d)

    assert flat["writing.max_sentence_words"] == 30
    assert flat["max_sentence_words"] == 30
    assert flat["writing.english_variant"] == "british"
    assert flat["english_variant"] == "british"


def test_flatten_preserves_full_path_on_collision():
    """Test that full-path keys take precedence over short keys on collision."""
    d = {"a": 1, "a.b": 2}
    flat = _flatten(d)

    assert flat["a"] == 1  # Full path 'a' should not be overwritten
    assert flat["b"] == 2  # Short key 'b' from 'a.b' should be added


def test_assembler_handles_missing_rule_gracefully():
    """Test that assembler skips missing rule files without error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "# Test\n{{RULES_INJECTION_POINT}}\n"
        )
        (skill_dir / "manifest.yaml").write_text(
            "rules:\n  - nonexistent/rule\n"
        )

        assembler = Assembler(Path("core"))
        result = assembler.assemble("nature", skill_dir)
        # Should not raise, just skip the missing rule
        assert "# Test" in result


def test_assembler_without_injection_point():
    """Test that assembler returns content unchanged when no injection point."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "# Test Skill\nNo injection point here.\n"
        )

        assembler = Assembler(Path("core"))
        result = assembler.assemble("nature", skill_dir)
        assert "No injection point here." in result
        assert "# Test Skill" in result


def test_load_journal_config_not_found():
    """Test that loading a non-existent journal raises FileNotFoundError."""
    try:
        load_journal_config("nonexistent", Path("core/journals"))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass
