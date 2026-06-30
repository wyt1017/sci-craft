"""Tests for engine/validator.py - Static and runtime validation."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from engine.validator import StaticValidation, RuntimeValidation, ValidationError


def test_static_validation_init():
    """Test StaticValidation initialization."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        core_dir.mkdir(parents=True, exist_ok=True)
        skills_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        validator = StaticValidation(core_dir, skills_dir)
        assert validator.core_dir == core_dir
        assert validator.skills_dir == skills_dir


def test_validate_manifest_missing():
    """Test manifest validation when file is missing."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        validator = StaticValidation(core_dir, skills_dir)
        errors = validator.validate_manifest(skill_dir)

        assert len(errors) > 0
        assert any("manifest.yaml not found" in e.message for e in errors)


def test_validate_manifest_required_fields():
    """Test manifest validation for required fields."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        # Write incomplete manifest
        manifest = {"id": "test-skill"}  # Missing name, version, status
        with open(skill_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        validator = StaticValidation(core_dir, skills_dir)
        errors = validator.validate_manifest(skill_dir)

        assert len(errors) >= 2
        assert any("Missing required field: name" in e.message for e in errors)
        assert any("Missing required field: version" in e.message for e in errors)
        assert any("Missing required field: status" in e.message for e in errors)


def test_validate_manifest_invalid_status():
    """Test manifest validation for invalid status."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        manifest = {
            "id": "test-skill",
            "name": "Test Skill",
            "version": "1.0.0",
            "status": "invalid_status",
        }
        with open(skill_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        validator = StaticValidation(core_dir, skills_dir)
        errors = validator.validate_manifest(skill_dir)

        assert any("Non-standard status" in e.message for e in errors)


def test_validate_rules_refs():
    """Test validation of rule references."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        skill_dir = skills_dir / "test-skill"
        rules_dir = core_dir / "rules"

        skill_dir.mkdir(parents=True, exist_ok=True)
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "writing").mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)

        # Write valid rule
        with open(rules_dir / "writing" / "sentence-length.md", "w") as f:
            f.write("# Sentence Length Rule")

        # Write manifest with mixed valid/invalid refs
        manifest = {
            "id": "test-skill",
            "name": "Test Skill",
            "version": "1.0.0",
            "status": "active",
            "rules": [
                "writing/sentence-length.md",  # Valid
                "writing/nonexistent.md",  # Invalid
            ],
        }
        with open(skill_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        validator = StaticValidation(core_dir, skills_dir)
        errors = validator.validate_rules_refs(skill_dir)

        assert len(errors) == 1
        assert "nonexistent.md" in errors[0].message


def test_runtime_validation_residual_placeholders():
    """Test runtime validation for residual placeholders."""
    validator = RuntimeValidation()

    content = "Hello {{name}}, welcome to {{place}}"
    errors = validator.validate_rendered_output(content)

    assert len(errors) > 0
    assert any("Residual template placeholder" in e.message for e in errors)


def test_runtime_validation_clean_content():
    """Test runtime validation with clean content."""
    validator = RuntimeValidation()

    content = "Hello John, welcome to London"
    errors = validator.validate_rendered_output(content)

    assert len(errors) == 0


def test_runtime_validation_residual_blocks():
    """Test runtime validation for residual Jinja2 blocks."""
    validator = RuntimeValidation()

    content = "{% if condition %}Some content{% endif %}"
    errors = validator.validate_rendered_output(content)

    assert len(errors) > 0
    assert any("Residual template block" in e.message for e in errors)


def test_validation_error_string():
    """Test ValidationError string representation."""
    error = ValidationError("error", "Test error message", Path("/test/file.yaml"), 10)
    error_str = str(error)

    assert "[ERROR]" in error_str
    assert "Test error message" in error_str
    assert "file.yaml:10" in error_str


def test_validate_skill_full():
    """Test full skill validation."""
    with TemporaryDirectory() as tmpdir:
        core_dir = Path(tmpdir) / "core"
        skills_dir = Path(tmpdir) / "skills"
        skill_dir = skills_dir / "test-skill"

        skill_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        # Write complete manifest
        manifest = {
            "id": "test-skill",
            "name": "Test Skill",
            "version": "1.0.0",
            "status": "active",
            "triggers": ["test"],
        }
        with open(skill_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        # Write journal config
        journal_config = {"name": "nature"}
        with open(core_dir / "journals" / "nature.yaml", "w") as f:
            yaml.dump(journal_config, f)

        # Write SKILL.md
        with open(skill_dir / "SKILL.md", "w") as f:
            f.write("# Test Skill")

        validator = StaticValidation(core_dir, skills_dir)
        errors = validator.validate_skill(skill_dir, "nature")

        # Should have no errors for complete valid skill
        error_level_errors = [e for e in errors if e.level == "error"]
        assert len(error_level_errors) == 0