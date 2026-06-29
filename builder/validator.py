"""Skill validator — checks skill directory completeness and correctness."""
import re
from pathlib import Path

import yaml

REQUIRED_MANIFEST_FIELDS = ["name", "version", "status", "triggers"]
VALID_STATUSES = {"stable", "beta", "experimental", "draft"}


class ValidationError:
    """A single validation error."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"ValidationError({self.message!r})"


def validate_skill(skill_dir: Path) -> list[ValidationError]:
    """Validate a skill directory.

    Checks:
    1. SKILL.md exists and is non-empty
    2. manifest.yaml exists and is valid YAML
    3. manifest.yaml has all required fields
    4. Referenced files exist
    5. Version follows semantic versioning
    6. Status is a valid value
    7. Triggers is a non-empty list or string

    Args:
        skill_dir: Path to the skill directory.

    Returns:
        List of ValidationError objects. Empty list means valid.
    """
    errors: list[ValidationError] = []

    # 1. SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(ValidationError("SKILL.md is missing"))
    elif skill_md.read_text(encoding="utf-8").strip() == "":
        errors.append(ValidationError("SKILL.md is empty"))

    # 2. manifest.yaml
    manifest_path = skill_dir / "manifest.yaml"
    manifest = None
    if not manifest_path.exists():
        errors.append(ValidationError("manifest.yaml is missing"))
    else:
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = yaml.safe_load(f)
            if not isinstance(manifest, dict):
                errors.append(ValidationError("manifest.yaml must be a YAML mapping"))
        except yaml.YAMLError as e:
            errors.append(ValidationError(f"manifest.yaml has invalid YAML: {e}"))

    # 3. Required manifest fields and format validation
    if isinstance(manifest, dict):
        for field in REQUIRED_MANIFEST_FIELDS:
            if field not in manifest:
                errors.append(ValidationError(f"manifest.yaml missing required field: {field}"))
            else:
                # Validate field formats
                if field == "version":
                    version = manifest[field]
                    if not isinstance(version, str) or not re.match(r"^\d+\.\d+\.\d+$", version):
                        errors.append(ValidationError(
                            f"manifest.yaml 'version' must follow semantic versioning (e.g., '1.0.0'), got: {version!r}"
                        ))
                elif field == "status":
                    status = manifest[field]
                    if status not in VALID_STATUSES:
                        errors.append(ValidationError(
                            f"manifest.yaml 'status' must be one of {sorted(VALID_STATUSES)}, got: {status!r}"
                        ))
                elif field == "triggers":
                    triggers = manifest[field]
                    if not isinstance(triggers, (list, str)) or (isinstance(triggers, list) and len(triggers) == 0):
                        errors.append(ValidationError(
                            "manifest.yaml 'triggers' must be a non-empty list or a non-empty string"
                        ))

        # 4. Referenced files exist
        references = manifest.get("references", [])
        if references:
            for ref in references:
                ref_path = skill_dir / "references" / ref
                if not ref_path.exists():
                    # Also check if ref is relative to skill_dir directly
                    alt_path = skill_dir / ref
                    if not alt_path.exists():
                        errors.append(ValidationError(f"Referenced file not found: {ref}"))

    return errors
