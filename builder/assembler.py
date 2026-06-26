"""Skill assembler — combines journal config + rules + SKILL.md template."""
from pathlib import Path

import yaml


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, returning a new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _flatten(d: dict, parent_key: str = "", sep: str = ".") -> dict[str, object]:
    """Flatten a nested dict into dot-notation keys for template rendering.

    Produces both full-path keys (e.g. ``writing.max_sentence_words``) and
    short leaf keys (e.g. ``max_sentence_words``) so that templates can use
    the convenient short form.  Full-path keys take precedence on collision.
    """
    items: list[tuple[str, object]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    result = dict(items)
    # Add short (leaf) keys for convenience in templates
    for key, value in list(result.items()):
        parts = key.split(sep)
        if len(parts) > 1 and parts[-1] not in result:
            result[parts[-1]] = value
    return result


def load_journal_config(journal: str, journals_dir: Path) -> dict:
    """Load a journal config, inheriting from _base.yaml.

    Args:
        journal: Journal name (e.g., "nature", "science").
        journals_dir: Path to core/journals/ directory.

    Returns:
        Merged configuration dict.
    """
    base_path = journals_dir / "_base.yaml"
    journal_path = journals_dir / f"{journal}.yaml"

    with open(base_path, encoding="utf-8") as f:
        base_config = yaml.safe_load(f)

    if not journal_path.exists():
        raise FileNotFoundError(f"Journal config not found: {journal_path}")

    with open(journal_path, encoding="utf-8") as f:
        journal_config = yaml.safe_load(f)

    return _deep_merge(base_config, journal_config)


class Assembler:
    """Assembles a SKILL.md by rendering templates with journal config and rules."""

    def __init__(self, core_dir: Path):
        self.core_dir = core_dir
        self.journals_dir = core_dir / "journals"
        self.rules_dir = core_dir / "rules"

    def assemble(self, journal: str, skill_dir: Path) -> str:
        """Assemble the final SKILL.md content.

        Args:
            journal: Target journal name.
            skill_dir: Path to the skill directory containing SKILL.md template.

        Returns:
            Rendered SKILL.md content as string.
        """
        config = load_journal_config(journal, self.journals_dir)
        flat_config = _flatten(config)

        skill_md_path = skill_dir / "SKILL.md"
        if not skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        content = skill_md_path.read_text(encoding="utf-8")

        # Render template variables: {{key}} -> value
        for key, value in flat_config.items():
            placeholder = "{{" + key + "}}"
            if placeholder in content:
                content = content.replace(placeholder, str(value))

        # Render lists like {{font_sans_list}} as Python list repr
        # (for rcParams in figure rules)
        for key, value in flat_config.items():
            placeholder = "{{" + key + "_list}}"
            if placeholder in content:
                content = content.replace(placeholder, repr(value) if isinstance(value, list) else str(value))

        # Inject rules at RULES_INJECTION_POINT
        content = self._inject_rules(content, skill_dir, config)

        return content

    def _inject_rules(self, content: str, skill_dir: Path, config: dict) -> str:
        """Inject referenced rules at the injection point."""
        injection_point = "{{RULES_INJECTION_POINT}}"
        if injection_point not in content:
            return content

        manifest_path = skill_dir / "manifest.yaml"
        if not manifest_path.exists():
            return content.replace(injection_point, "")

        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        rule_refs = manifest.get("rules", [])
        if not rule_refs:
            return content.replace(injection_point, "")

        rule_sections: list[str] = []
        flat_config = _flatten(config)

        for rule_ref in rule_refs:
            rule_path = self.rules_dir / f"{rule_ref}.md"
            if not rule_path.exists():
                continue
            rule_content = rule_path.read_text(encoding="utf-8")
            # Render any template variables in the rule
            for key, value in flat_config.items():
                placeholder = "{{" + key + "}}"
                if placeholder in rule_content:
                    rule_content = rule_content.replace(placeholder, str(value))
            rule_sections.append(rule_content)

        return content.replace(injection_point, "\n\n---\n\n".join(rule_sections))
