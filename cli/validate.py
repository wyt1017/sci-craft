"""Validate command for sci-craft CLI."""

import argparse
from pathlib import Path

from engine.validator import StaticValidation


def find_project_root() -> Path:
    """Find project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "skills").exists() and (current / "core").exists():
            return current
        current = current.parent
    return Path.cwd()


def validate_all_skills(project_dir: Path, journal: str) -> tuple[int, int]:
    """Validate all skills.

    Args:
        project_dir: Project root directory
        journal: Journal name for template variable validation

    Returns:
        Tuple of (total_skills, skills_with_errors)
    """
    skills_dir = project_dir / "skills"
    core_dir = project_dir / "core"

    validator = StaticValidation(core_dir, skills_dir)

    total = 0
    with_errors = 0

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
            if (skill_dir / "manifest.yaml").exists():
                total += 1
                errors = validator.validate_skill(skill_dir, journal)

                if errors:
                    with_errors += 1
                    print(f"\n{skill_dir.name}:")
                    for error in errors:
                        print(f"  {error}")
                else:
                    print(f"✓ {skill_dir.name}: OK")

    return total, with_errors


def validate_single_skill(project_dir: Path, skill_name: str, journal: str) -> bool:
    """Validate a single skill.

    Args:
        project_dir: Project root directory
        skill_name: Skill name
        journal: Journal name

    Returns:
        True if no errors, False otherwise
    """
    skills_dir = project_dir / "skills"
    core_dir = project_dir / "core"
    skill_dir = skills_dir / skill_name

    if not skill_dir.exists():
        print(f"ERROR: Skill not found: {skill_name}")
        return False

    validator = StaticValidation(core_dir, skills_dir)
    errors = validator.validate_skill(skill_dir, journal)

    if errors:
        print(f"\nValidation errors for {skill_name}:")
        for error in errors:
            print(f"  {error}")
        return False

    print(f"✓ {skill_name}: All validations passed")
    return True


def main():
    """Main entry point for validate command."""
    parser = argparse.ArgumentParser(description="Validate sci-craft skills")
    parser.add_argument(
        "--skill",
        "-s",
        help="Validate a specific skill (optional)",
    )
    parser.add_argument(
        "--journal",
        "-j",
        default="nature",
        help="Journal for template variable validation (default: nature)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code on warnings",
    )

    args = parser.parse_args()

    project_dir = find_project_root()

    print(f"Project: {project_dir}")
    print(f"Journal: {args.journal}")

    if args.skill:
        success = validate_single_skill(project_dir, args.skill, args.journal)
        return 0 if success else 1
    else:
        total, with_errors = validate_all_skills(project_dir, args.journal)
        print(f"\nSummary: {total - with_errors}/{total} skills passed validation")
        if with_errors > 0:
            return 1
        return 0


if __name__ == "__main__":
    exit(main())