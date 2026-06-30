"""Dependency-level caching system."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DepNode:
    """Dependency node for a skill."""

    manifest_hash: str
    skill_md_hash: str
    rules_hashes: list[str]
    references_hashes: list[str]
    journal_config_hash: str


class DependencyCache:
    """Dependency-level cache manager."""

    CACHE_FILE = Path(".sci_craft_cache.json")

    def __init__(self, project_dir: Path):
        """Initialize cache manager.

        Args:
            project_dir: Project root directory
        """
        self.project_dir = project_dir
        self.cache_path = project_dir / self.CACHE_FILE
        self._cache: dict = self._load_cache()

    def _load_cache(self) -> dict:
        """Load cache from disk."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"skills": {}}
        return {"skills": {}}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash string
        """
        if not file_path.exists():
            return ""

        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()

    def compute_dependency_graph(self, skill_dir: Path, journal: str, journals_dir: Path, rules_dir: Path) -> DepNode:
        """Compute dependency graph for a skill.

        Args:
            skill_dir: Path to skill directory
            journal: Journal name
            journals_dir: Path to journals directory
            rules_dir: Path to rules directory

        Returns:
            DepNode with dependency hashes
        """
        # Manifest hash
        manifest_path = skill_dir / "manifest.yaml"
        manifest_hash = self._compute_file_hash(manifest_path)

        # SKILL.md hash
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_hash = self._compute_file_hash(skill_md_path)

        # Rules hashes
        rules_hashes = []
        manifest = {}
        if manifest_path.exists():
            import yaml
            with open(manifest_path, encoding="utf-8") as f:
                manifest = yaml.safe_load(f) or {}

        for rule_ref in manifest.get("rules", []):
            rule_path = rules_dir / rule_ref
            rules_hashes.append(self._compute_file_hash(rule_path))

        # References hashes
        references_hashes = []
        references_dir = skill_dir / "references"
        if references_dir.exists():
            for ref_file in references_dir.glob("*"):
                if ref_file.is_file() and ref_file.name != ".gitkeep":
                    references_hashes.append(self._compute_file_hash(ref_file))

        # Journal config hash
        journal_config_path = journals_dir / f"{journal}.yaml"
        base_config_path = journals_dir / "_base.yaml"
        combined_hash = self._compute_file_hash(base_config_path) + self._compute_file_hash(journal_config_path)
        journal_config_hash = hashlib.md5(combined_hash.encode()).hexdigest()

        return DepNode(
            manifest_hash=manifest_hash,
            skill_md_hash=skill_md_hash,
            rules_hashes=rules_hashes,
            references_hashes=references_hashes,
            journal_config_hash=journal_config_hash,
        )

    def compute_cache_hash(self, dep_node: DepNode) -> str:
        """Compute overall hash from dependency node.

        Args:
            dep_node: Dependency node

        Returns:
            Combined hash string
        """
        combined = (
            dep_node.manifest_hash +
            dep_node.skill_md_hash +
            "".join(dep_node.rules_hashes) +
            "".join(dep_node.references_hashes) +
            dep_node.journal_config_hash
        )
        return hashlib.md5(combined.encode()).hexdigest()

    def should_rebuild(self, skill_name: str, journal: str, dep_node: DepNode) -> bool:
        """Check if skill needs rebuilding.

        Args:
            skill_name: Skill name/id
            journal: Journal name
            dep_node: Dependency node

        Returns:
            True if rebuild needed, False if cache is valid
        """
        current_hash = self.compute_cache_hash(dep_node)

        cached = self._cache.get("skills", {}).get(skill_name, {}).get(journal, {})
        cached_hash = cached.get("hash", "")

        return current_hash != cached_hash

    def update_cache(self, skill_name: str, journal: str, dep_node: DepNode) -> None:
        """Update cache record for a skill.

        Args:
            skill_name: Skill name/id
            journal: Journal name
            dep_node: Dependency node
        """
        current_hash = self.compute_cache_hash(dep_node)

        if "skills" not in self._cache:
            self._cache["skills"] = {}

        if skill_name not in self._cache["skills"]:
            self._cache["skills"][skill_name] = {}

        self._cache["skills"][skill_name][journal] = {
            "hash": current_hash,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "deps": {
                "manifest": dep_node.manifest_hash,
                "skill_md": dep_node.skill_md_hash,
                "rules": dep_node.rules_hashes,
                "references": dep_node.references_hashes,
            },
        }

        self._save_cache()

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        skills = self._cache.get("skills", {})
        total_cached = sum(len(journals) for journals in skills.values())
        return {
            "total_skills": len(skills),
            "total_cached_builds": total_cached,
            "cache_file": str(self.cache_path),
        }

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache = {"skills": {}}
        self._save_cache()

    def get_cached_skills(self) -> list[str]:
        """Get list of cached skill names.

        Returns:
            List of skill names
        """
        return list(self._cache.get("skills", {}).keys())
