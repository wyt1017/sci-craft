"""Build command for sci-craft CLI."""

import argparse
from pathlib import Path

from engine.cache import DependencyCache
from engine.planner import BuildPlanner
from engine.renderer import Renderer
from engine.validator import RuntimeValidation, StaticValidation


def find_project_root() -> Path:
    """Find project root directory."""
    # Start from current directory and look for markers
    current = Path.cwd()
    while current != current.parent:
        if (current / "skills").exists() and (current / "core").exists():
            return current
        current = current.parent
    return Path.cwd()


def build_single_skill(
    skill_name: str,
    journal: str,
    project_dir: Path,
    output_dir: Path,
    force: bool = False,
) -> bool:
    """Build a single skill for a journal.

    Args:
        skill_name: Skill name
        journal: Journal name
        project_dir: Project root directory
        output_dir: Output directory for built files
        force: Force rebuild

    Returns:
        True if build succeeded, False otherwise
    """
    core_dir = project_dir / "core"
    skills_dir = project_dir / "skills"
    skill_dir = skills_dir / skill_name

    if not skill_dir.exists():
        print(f"ERROR: Skill not found: {skill_name}")
        return False

    # Static validation
    static_validator = StaticValidation(core_dir, skills_dir)
    errors = static_validator.validate_skill(skill_dir, journal)
    if errors:
        print(f"Static validation errors for {skill_name}:")
        for error in errors:
            print(f"  {error}")
        # Continue despite warnings, but stop on errors
        if any(e.level == "error" for e in errors):
            return False

    # Check cache
    cache = DependencyCache(project_dir)
    dep_node = cache.compute_dependency_graph(
        skill_dir=skill_dir,
        journal=journal,
        journals_dir=core_dir / "journals",
        rules_dir=core_dir / "rules",
    )

    if not force and not cache.should_rebuild(skill_name, journal, dep_node):
        print(f"SKIP: {skill_name} (cache valid)")
        return True

    # Render
    renderer = Renderer(core_dir)
    try:
        rendered = renderer.render_skill(journal, skill_dir)
    except Exception as e:
        print(f"ERROR: Failed to render {skill_name}: {e}")
        return False

    # Runtime validation
    runtime_validator = RuntimeValidation()
    errors = runtime_validator.validate_rendered_output(rendered)
    if errors:
        print(f"Runtime validation errors for {skill_name}:")
        for error in errors:
            print(f"  {error}")
        return False

    # Write output
    output_path = output_dir / journal / skill_name / "SKILL.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    # Update cache
    cache.update_cache(skill_name, journal, dep_node)

    print(f"BUILD: {skill_name} -> {output_path}")
    return True


def build_all_skills(
    journal: str,
    project_dir: Path,
    output_dir: Path,
    incremental: bool = False,
) -> int:
    """Build all skills for a journal.

    Args:
        journal: Journal name
        project_dir: Project root directory
        output_dir: Output directory
        incremental: Use incremental build with cache

    Returns:
        Number of successfully built skills
    """
    skills_dir = project_dir / "skills"
    core_dir = project_dir / "core"

    # Discover all skills
    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            if (item / "manifest.yaml").exists():
                skills.append(item.name)

    if incremental:
        # Use planner for incremental build
        cache = DependencyCache(project_dir)
        planner = BuildPlanner(cache)
        plan = planner.plan_incremental(
            journal=journal,
            skills_dir=skills_dir,
            journals_dir=core_dir / "journals",
            rules_dir=core_dir / "rules",
        )

        print(f"Build plan for {journal}:")
        print(f"  Rebuild: {len(plan.rebuild)} skills")
        print(f"  Skip: {len(plan.skip)} skills")

        success_count = 0
        for skill_name in plan.order:
            if skill_name in plan.skip:
                print(f"SKIP: {skill_name}")
                success_count += 1
            else:
                if build_single_skill(skill_name, journal, project_dir, output_dir):
                    success_count += 1
        return success_count
    else:
        # Full build
        success_count = 0
        for skill_name in skills:
            if build_single_skill(skill_name, journal, project_dir, output_dir, force=True):
                success_count += 1
        return success_count


def main():
    """Main entry point for build command."""
    parser = argparse.ArgumentParser(description="Build sci-craft skills")
    parser.add_argument(
        "--journal",
        "-j",
        required=True,
        help="Journal name (e.g., nature, science)",
    )
    parser.add_argument(
        "--skill",
        "-s",
        help="Build a specific skill (optional)",
    )
    parser.add_argument(
        "--platform",
        "-p",
        default="trae",
        help="Platform adapter (default: trae)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory (default: build/)",
    )
    parser.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Use incremental build with cache",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force rebuild, ignore cache",
    )

    args = parser.parse_args()

    project_dir = find_project_root()
    output_dir = Path(args.output) if args.output else project_dir / "build"

    print(f"Project: {project_dir}")
    print(f"Journal: {args.journal}")
    print(f"Output: {output_dir}")

    if args.skill:
        # Build single skill
        success = build_single_skill(
            skill_name=args.skill,
            journal=args.journal,
            project_dir=project_dir,
            output_dir=output_dir,
            force=args.force,
        )
        if success:
            print(f"\n✓ Successfully built {args.skill}")
        else:
            print(f"\n✗ Failed to build {args.skill}")
            return 1
    else:
        # Build all skills
        success_count = build_all_skills(
            journal=args.journal,
            project_dir=project_dir,
            output_dir=output_dir,
            incremental=args.incremental,
        )
        total = len(list((project_dir / "skills").glob("*")))
        if not args.incremental:
            total = sum(
                1
                for d in (project_dir / "skills").glob("*")
                if d.is_dir() and not d.name.startswith("_") and (d / "manifest.yaml").exists()
            )
        print(f"\n✓ Successfully built {success_count}/{total} skills")

    return 0


if __name__ == "__main__":
    exit(main())
