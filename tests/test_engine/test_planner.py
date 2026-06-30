"""Tests for engine/planner.py - Build plan generation."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from engine.cache import DependencyCache, DepNode
from engine.planner import BuildPlanner, BuildPlan


def test_build_plan():
    """Test BuildPlan dataclass."""
    plan = BuildPlan(
        rebuild=["skill-a", "skill-c"],
        skip=["skill-b"],
        order=["skill-a", "skill-b", "skill-c"],
    )

    assert len(plan.rebuild) == 2
    assert len(plan.skip) == 1
    assert len(plan.order) == 3


def test_build_planner_init():
    """Test BuildPlanner initialization."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)
        planner = BuildPlanner(cache)

        assert planner.cache == cache


def test_plan_force_rebuild():
    """Test plan generation with force rebuild."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)
        planner = BuildPlanner(cache)

        plan = planner.plan(
            journal="nature",
            skills=["skill-a", "skill-b", "skill-c"],
            skills_dir=Path(tmpdir),
            journals_dir=Path(tmpdir),
            rules_dir=Path(tmpdir),
            force=True,
        )

        # Force rebuild should rebuild all
        assert plan.rebuild == ["skill-a", "skill-b", "skill-c"]
        assert plan.skip == []


def test_plan_with_cache():
    """Test plan generation with cache."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        core_dir = project_dir / "core"
        skills_dir = project_dir / "skills"

        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        # Create skill1 directory
        skill1_dir = skills_dir / "skill1"
        skill1_dir.mkdir(parents=True, exist_ok=True)

        manifest = {"id": "skill1", "name": "Skill 1", "version": "1.0.0", "status": "active"}
        with open(skill1_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        with open(skill1_dir / "SKILL.md", "w") as f:
            f.write("# Skill 1")

        # Create skill2 directory (not yet cached)
        skill2_dir = skills_dir / "skill2"
        skill2_dir.mkdir(parents=True, exist_ok=True)

        manifest2 = {"id": "skill2", "name": "Skill 2", "version": "1.0.0", "status": "active"}
        with open(skill2_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest2, f)

        with open(skill2_dir / "SKILL.md", "w") as f:
            f.write("# Skill 2")

        # Create journal config
        with open(core_dir / "journals" / "nature.yaml", "w") as f:
            yaml.dump({"name": "nature"}, f)

        cache = DependencyCache(project_dir)

        # Cache skill1
        dep_node = cache.compute_dependency_graph(
            skill_dir=skill1_dir,
            journal="nature",
            journals_dir=core_dir / "journals",
            rules_dir=core_dir / "rules",
        )
        cache.update_cache("skill1", "nature", dep_node)

        planner = BuildPlanner(cache)
        plan = planner.plan(
            journal="nature",
            skills=["skill1", "skill2"],
            skills_dir=skills_dir,
            journals_dir=core_dir / "journals",
            rules_dir=core_dir / "rules",
            force=False,
        )

        # skill1 should be skipped (cached)
        # skill2 should be rebuilt (not cached)
        assert "skill1" in plan.skip
        assert "skill2" in plan.rebuild


def test_plan_incremental():
    """Test incremental build plan."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        core_dir = project_dir / "core"
        skills_dir = project_dir / "skills"

        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)

        # Create multiple skills
        for i in range(1, 4):
            skill_dir = skills_dir / f"skill{i}"
            skill_dir.mkdir(parents=True, exist_ok=True)

            manifest = {
                "id": f"skill{i}",
                "name": f"Skill {i}",
                "version": "1.0.0",
                "status": "active",
            }
            with open(skill_dir / "manifest.yaml", "w") as f:
                yaml.dump(manifest, f)

            with open(skill_dir / "SKILL.md", "w") as f:
                f.write(f"# Skill {i}")

        # Create journal config
        with open(core_dir / "journals" / "nature.yaml", "w") as f:
            yaml.dump({"name": "nature"}, f)

        cache = DependencyCache(project_dir)
        planner = BuildPlanner(cache)

        plan = planner.plan_incremental(
            journal="nature",
            skills_dir=skills_dir,
            journals_dir=core_dir / "journals",
            rules_dir=core_dir / "rules",
        )

        # Should discover all 3 skills
        assert len(plan.order) == 3
        assert "skill1" in plan.order
        assert "skill2" in plan.order
        assert "skill3" in plan.order


def test_plan_skill_not_exist():
    """Test plan when skill doesn't exist."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)
        planner = BuildPlanner(cache)

        plan = planner.plan(
            journal="nature",
            skills=["nonexistent-skill"],
            skills_dir=Path(tmpdir),
            journals_dir=Path(tmpdir),
            rules_dir=Path(tmpdir),
            force=False,
        )

        # Nonexistent skill should not appear in rebuild or skip
        assert "nonexistent-skill" not in plan.rebuild
        assert "nonexistent-skill" not in plan.skip