"""Static and runtime validation for skills."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ValidationError:
    """Validation error representation."""

    level: str  # "error" or "warning"
    message: str
    file_path: Optional[Path] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        location = ""
        if self.file_path:
            location = f" [{self.file_path}"
            if self.line:
                location += f":{self.line}"
            location += "]"
        return f"[{self.level.upper()}]{location} {self.message}"


class StaticValidation:
    """Static validation - runs before build."""

    def __init__(self, core_dir: Path, skills_dir: Path):
        """Initialize static validator.

        Args:
            core_dir: Path to core directory
            skills_dir: Path to skills directory
        """
        self.core_dir = core_dir
        self.skills_dir = skills_dir
        self.rules_dir = core_dir / "rules"
        self.journals_dir = core_dir / "journals"

    def validate_manifest(self, skill_dir: Path) -> list[ValidationError]:
        """Validate manifest.yaml structure.

        Checks:
        - Required fields: id, name, version, status
        - Version format (semver)
        - Status value (active/deprecated/draft)
        - Triggers non-empty

        Args:
            skill_dir: Path to skill directory

        Returns:
            List of validation errors
        """
        errors = []
        manifest_path = skill_dir / "manifest.yaml"

        if not manifest_path.exists():
            errors.append(ValidationError("error", "manifest.yaml not found", manifest_path))
            return errors

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            errors.append(ValidationError("error", f"Invalid YAML: {e}", manifest_path))
            return errors

        # Check required fields (name can substitute for id in legacy manifests)
        required_fields = ["name", "version", "status"]
        for field in required_fields:
            if field not in manifest:
                errors.append(ValidationError("error", f"Missing required field: {field}", manifest_path))

        # Check for id (optional but recommended for new manifests)
        if "id" not in manifest and "name" not in manifest:
            errors.append(ValidationError("error", "Missing identifier: either 'id' or 'name' field required", manifest_path))

        # Validate version format (semver)
        if "version" in manifest:
            version_pattern = r"^\d+\.\d+\.\d+$"
            if not re.match(version_pattern, str(manifest["version"])):
                errors.append(ValidationError("warning", f"Version should be semver format (x.y.z): {manifest['version']}", manifest_path))

        # Validate status
        if "status" in manifest:
            valid_statuses = ["active", "deprecated", "draft", "stable", "beta", "alpha", "experimental"]
            if manifest["status"] not in valid_statuses:
                errors.append(ValidationError("warning", f"Non-standard status: {manifest['status']}. Recommended: active, deprecated, draft", manifest_path))

        # Check triggers non-empty
        if "triggers" in manifest:
            if not manifest["triggers"]:
                errors.append(ValidationError("warning", "Triggers list is empty", manifest_path))

        return errors

    def validate_rules_refs(self, skill_dir: Path) -> list[ValidationError]:
        """Validate that referenced rules exist.

        Args:
            skill_dir: Path to skill directory

        Returns:
            List of validation errors
        """
        errors = []
        manifest_path = skill_dir / "manifest.yaml"

        if not manifest_path.exists():
            return errors

        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

        rules = manifest.get("rules", [])
        for rule_ref in rules:
            # Try with .md extension if not present
            rule_path = self.rules_dir / rule_ref
            if not rule_path.exists():
                # Try adding .md extension
                if not rule_ref.endswith(".md"):
                    rule_path = self.rules_dir / (rule_ref + ".md")
                if not rule_path.exists():
                    errors.append(ValidationError("error", f"Referenced rule not found: {rule_ref}", manifest_path))

        return errors

    def validate_template_variables(self, skill_dir: Path, journal: str) -> list[ValidationError]:
        """Validate template variables in SKILL.md exist in config.

        Args:
            skill_dir: Path to skill directory
            journal: Journal name

        Returns:
            List of validation errors
        """
        errors = []
        skill_md_path = skill_dir / "SKILL.md"

        if not skill_md_path.exists():
            return errors

        # Load journal config
        journal_path = self.journals_dir / f"{journal}.yaml"
        base_path = self.journals_dir / "_base.yaml"

        config = {}
        if base_path.exists():
            with open(base_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        if journal_path.exists():
            with open(journal_path, encoding="utf-8") as f:
                journal_config = yaml.safe_load(f) or {}
                config.update(journal_config)

        # Extract template variables from SKILL.md
        content = skill_md_path.read_text(encoding="utf-8")

        # Find all {{ variable }} patterns
        var_pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\}\}"
        variables = set(re.findall(var_pattern, content))

        # Check each variable exists in config
        def get_nested_value(d: dict, key: str):
            keys = key.split(".")
            value = d
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None
            return value

        for var in variables:
            # Skip built-in template functions
            if var in ("rules", "include_rule", "journal_is"):
                continue

            value = get_nested_value(config, var)
            if value is None:
                errors.append(ValidationError("warning", f"Template variable not found in config: {var}", skill_md_path))

        return errors

    def validate_references(self, skill_dir: Path) -> list[ValidationError]:
        """Validate that referenced files in references/ exist.

        Args:
            skill_dir: Path to skill directory

        Returns:
            List of validation errors
        """
        errors = []
        manifest_path = skill_dir / "manifest.yaml"

        if not manifest_path.exists():
            return errors

        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}

        references = manifest.get("references", [])
        references_dir = skill_dir / "references"

        for ref in references:
            ref_path = references_dir / ref
            if not ref_path.exists():
                errors.append(ValidationError("warning", f"Referenced file not found: references/{ref}", manifest_path))

        return errors

    def validate_skill(self, skill_dir: Path, journal: str) -> list[ValidationError]:
        """Run all static validations on a skill.

        Args:
            skill_dir: Path to skill directory
            journal: Journal name

        Returns:
            List of validation errors
        """
        errors = []
        errors.extend(self.validate_manifest(skill_dir))
        errors.extend(self.validate_rules_refs(skill_dir))
        errors.extend(self.validate_template_variables(skill_dir, journal))
        errors.extend(self.validate_references(skill_dir))
        return errors


class RuntimeValidation:
    """Runtime validation - runs after build/render."""

    def validate_rendered_output(self, rendered_content: str) -> list[ValidationError]:
        """Validate no residual placeholders in rendered output.

        Args:
            rendered_content: Rendered content string

        Returns:
            List of validation errors
        """
        errors = []

        # Find residual {{ }} placeholders
        placeholder_pattern = r"\{\{.*?\}\}"
        matches = re.findall(placeholder_pattern, rendered_content)

        if matches:
            for match in matches[:5]:  # Show first 5 matches
                errors.append(ValidationError("error", f"Residual template placeholder: {match}"))

        # Find residual {% %} blocks (unrendered control structures)
        block_pattern = r"\{%.*?%\}"
        block_matches = re.findall(block_pattern, rendered_content)

        if block_matches:
            for match in block_matches[:5]:
                errors.append(ValidationError("error", f"Residual template block: {match}"))

        return errors

    def validate_rule_injection(self, rendered_content: str, manifest: dict, rules_dir: Path) -> list[ValidationError]:
        """Validate that rules were injected correctly.

        Args:
            rendered_content: Rendered content string
            manifest: Skill manifest
            rules_dir: Path to rules directory

        Returns:
            List of validation errors
        """
        errors = []
        rules = manifest.get("rules", [])

        for rule_ref in rules:
            rule_path = rules_dir / rule_ref
            if not rule_path.exists():
                continue

            rule_content = rule_path.read_text(encoding="utf-8")
            # Check if at least part of rule content is in rendered output
            # (This is a simple heuristic, may need refinement)
            rule_heading = ""
            for line in rule_content.split("\n")[:5]:
                if line.startswith("#"):
                    rule_heading = line.strip()
                    break

            if rule_heading and rule_heading not in rendered_content:
                errors.append(ValidationError("warning", f"Rule heading not found in output: {rule_heading}"))

        return errors