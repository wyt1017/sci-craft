"""Build plan generator with cache integration."""

from dataclasses import dataclass
from pathlib import Path

from .cache import DependencyCache


@dataclass
class BuildPlan:
    """Build plan with execution order."""

    rebuild: list[str]  # Skills that need rebuilding
    skip: list[str]  # Skills that can be skipped (cache hit)
    order: list[str]  # Execution order (topologically sorted)


class BuildPlanner:
    """Build plan generator."""

    def __init__(self, cache: DependencyCache):
        """Initialize build planner.

        Args:
            cache: DependencyCache instance
        """
        self.cache = cache

    def plan(
        self,
        journal: str,
        skills: list[str],
        skills_dir: Path,
        journals_dir: Path,
        rules_dir: Path,
        force: bool = False,
    ) -> BuildPlan:
        """Generate build plan.

        Args:
            journal: Journal name
            skills: List of skill names to build
            skills_dir: Path to skills directory
            journals_dir: Path to journals directory
            rules_dir: Path to rules directory
            force: Force rebuild all skills

        Returns:
            BuildPlan with rebuild/skip lists and execution order
        """
        rebuild = []
        skip = []
        order = skills  # For now, maintain input order; could be topologically sorted later

        if force:
            # Force rebuild all
            return BuildPlan(rebuild=skills, skip=[], order=order)

        for skill_name in skills:
            skill_dir = skills_dir / skill_name

            if not skill_dir.exists():
                # Skill doesn't exist, can't build
                continue

            # Compute dependency node
            dep_node = self.cache.compute_dependency_graph(
                skill_dir=skill_dir,
                journal=journal,
                journals_dir=journals_dir,
                rules_dir=rules_dir,
            )

            # Check if rebuild needed
            if self.cache.should_rebuild(skill_name, journal, dep_node):
                rebuild.append(skill_name)
            else:
                skip.append(skill_name)

        return BuildPlan(rebuild=rebuild, skip=skip, order=order)

    def plan_incremental(
        self,
        journal: str,
        skills_dir: Path,
        journals_dir: Path,
        rules_dir: Path,
    ) -> BuildPlan:
        """Generate incremental build plan for all skills.

        Args:
            journal: Journal name
            skills_dir: Path to skills directory
            journals_dir: Path to journals directory
            rules_dir: Path to rules directory

        Returns:
            BuildPlan for all skills in skills_dir
        """
        # Discover all skills
        skills = []
        for item in skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # Check if it has manifest.yaml
                if (item / "manifest.yaml").exists():
                    skills.append(item.name)

        return self.plan(
            journal=journal,
            skills=skills,
            skills_dir=skills_dir,
            journals_dir=journals_dir,
            rules_dir=rules_dir,
            force=False,
        )
