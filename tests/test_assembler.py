"""Tests for builder/assembler.py"""
import tempfile
from pathlib import Path

import yaml

from builder.assembler import Assembler, load_journal_config


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
