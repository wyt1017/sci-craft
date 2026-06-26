"""Tests for builder/validator.py"""
import tempfile
from pathlib import Path

import yaml

from builder.validator import validate_skill, ValidationError


def _make_skill(tmpdir: Path, has_skill_md=True, has_manifest=True, has_readme=True, skill_md_content="# Skill", manifest_content=None, extra_files=None):
    """Helper to create a minimal skill directory."""
    skill_dir = tmpdir / "test-skill"
    skill_dir.mkdir(exist_ok=True)

    if has_skill_md:
        (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")
    if has_manifest:
        if manifest_content is None:
            manifest_content = {"name": "test-skill", "version": "0.1.0", "status": "stable", "triggers": ["test"]}
        (skill_dir / "manifest.yaml").write_text(yaml.dump(manifest_content), encoding="utf-8")
    if has_readme:
        (skill_dir / "README.md").write_text("# Test Skill README", encoding="utf-8")
    if extra_files:
        for name, content in extra_files.items():
            (skill_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (skill_dir / name).write_text(content, encoding="utf-8")

    return skill_dir


def test_valid_skill_passes():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill(Path(tmpdir))
        errors = validate_skill(skill_dir)
        assert errors == []


def test_missing_skill_md_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill(Path(tmpdir), has_skill_md=False)
        errors = validate_skill(skill_dir)
        assert any("SKILL.md" in str(e) for e in errors)


def test_empty_skill_md_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill(Path(tmpdir), skill_md_content="   \n")
        errors = validate_skill(skill_dir)
        assert any("SKILL.md" in str(e) for e in errors)


def test_missing_manifest_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill(Path(tmpdir), has_manifest=False)
        errors = validate_skill(skill_dir)
        assert any("manifest.yaml" in str(e) for e in errors)


def test_invalid_manifest_yaml_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = _make_skill(Path(tmpdir), has_manifest=True)
        # Overwrite with invalid YAML
        (skill_dir / "manifest.yaml").write_text(": invalid: yaml: [", encoding="utf-8")
        errors = validate_skill(skill_dir)
        assert any("manifest" in str(e).lower() for e in errors)


def test_missing_required_manifest_fields_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = {"name": "test-skill"}  # missing version, status, triggers
        skill_dir = _make_skill(Path(tmpdir), manifest_content=manifest)
        errors = validate_skill(skill_dir)
        assert any("version" in str(e) for e in errors)


def test_missing_referenced_file_fails():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = {
            "name": "test-skill",
            "version": "0.1.0",
            "status": "stable",
            "triggers": ["test"],
            "references": ["nonexistent.md"],
        }
        skill_dir = _make_skill(Path(tmpdir), manifest_content=manifest)
        errors = validate_skill(skill_dir)
        assert any("nonexistent" in str(e) for e in errors)


def test_existing_reference_passes():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = {
            "name": "test-skill",
            "version": "0.1.0",
            "status": "stable",
            "triggers": ["test"],
            "references": ["refs/guide.md"],
        }
        skill_dir = _make_skill(
            Path(tmpdir), manifest_content=manifest,
            extra_files={"references/refs/guide.md": "# Guide"},
        )
        errors = validate_skill(skill_dir)
        assert errors == []
