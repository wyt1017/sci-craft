"""Jinja2 template rendering engine."""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader


def flatten_config(config: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten nested config dict for template access.

    Example:
        {"writing": {"max_sentence_words": 25}} -> {"writing.max_sentence_words": 25}
    """
    items = []
    for k, v in config.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_config(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class Renderer:
    """Jinja2 template rendering engine."""

    def __init__(self, core_dir: Path):
        """Initialize the renderer.

        Args:
            core_dir: Path to the core directory containing journals, rules, templates
        """
        self.core_dir = core_dir
        self.journals_dir = core_dir / "journals"
        self.rules_dir = core_dir / "rules"
        self._env = Environment(
            loader=FileSystemLoader(str(core_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def load_journal_config(self, journal: str) -> dict:
        """Load and merge journal config with base config.

        Args:
            journal: Journal name (e.g., "nature", "science")

        Returns:
            Merged configuration dict
        """
        base_path = self.journals_dir / "_base.yaml"
        journal_path = self.journals_dir / f"{journal}.yaml"

        config = {}
        if base_path.exists():
            with open(base_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

        if journal_path.exists():
            with open(journal_path, encoding="utf-8") as f:
                journal_config = yaml.safe_load(f) or {}
                # Deep merge journal config over base
                config = self._deep_merge(config, journal_config)

        return config

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load_manifest(self, skill_dir: Path) -> dict:
        """Load skill manifest.yaml."""
        manifest_path = skill_dir / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_rules(self, rule_refs: list[str], config: dict) -> list[str]:
        """Load rule files referenced in manifest.

        Args:
            rule_refs: List of rule file paths (e.g., ["writing/sentence-length.md"])
            config: Journal config (for context, if needed)

        Returns:
            List of rule contents
        """
        rules = []
        for ref in rule_refs:
            rule_path = self.rules_dir / ref
            if rule_path.exists():
                rules.append(rule_path.read_text(encoding="utf-8"))
        return rules

    def _include_rule(self, name: str, config: dict) -> str:
        """Include a single rule file by name.

        Args:
            name: Rule file path (e.g., "writing/sentence-length.md")
            config: Journal config

        Returns:
            Rule file content
        """
        rule_path = self.rules_dir / name
        if rule_path.exists():
            return rule_path.read_text(encoding="utf-8")
        return f"<!-- Rule not found: {name} -->"

    def _build_context(self, config: dict, manifest: dict, skill_dir: Path) -> dict:
        """Build Jinja2 rendering context.

        Args:
            config: Journal config
            manifest: Skill manifest
            skill_dir: Skill directory path

        Returns:
            Context dict for template rendering
        """
        flat_config = flatten_config(config)
        return {
            **flat_config,
            **config,  # Also keep nested for direct access
            "rules": self._load_rules(manifest.get("rules", []), config),
            "include_rule": lambda name: self._include_rule(name, config),
            "journal_is": lambda j: config.get("name", "").lower() == j.lower(),
            "skill_dir": skill_dir,
            "manifest": manifest,
        }

    def render_skill(self, journal: str, skill_dir: Path) -> str:
        """Render a single skill's SKILL.md template.

        Args:
            journal: Journal name
            skill_dir: Path to skill directory

        Returns:
            Rendered content
        """
        config = self.load_journal_config(journal)
        template_path = skill_dir / "SKILL.md"

        if not template_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        template = self._env.from_string(template_path.read_text(encoding="utf-8"))
        manifest = self._load_manifest(skill_dir)
        context = self._build_context(config, manifest, skill_dir)
        return template.render(**context)

    def render_template(self, template_content: str, context: dict) -> str:
        """Render a template string with given context.

        Args:
            template_content: Template string content
            context: Rendering context

        Returns:
            Rendered content
        """
        template = self._env.from_string(template_content)
        return template.render(**context)