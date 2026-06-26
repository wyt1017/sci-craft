"""Build script — assemble and validate skills for a target journal and platform."""
import argparse
import shutil
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.trae import TraeAdapter
from builder.assembler import Assembler
from builder.validator import validate_skill


SKILLS_DIR = PROJECT_ROOT / "skills"
CORE_DIR = PROJECT_ROOT / "core"
OUTPUT_DIR = PROJECT_ROOT / "output"

ADAPTERS = {
    "trae": TraeAdapter,
}

BUILTIN_SKILLS = [
    d.name for d in SKILLS_DIR.iterdir()
    if d.is_dir() and d.name != "_shared" and (d / "manifest.yaml").exists()
]


def build_skill(skill_name: str, journal: str, platform: str, output_dir: Path) -> bool:
    """Build a single skill for a specific journal and platform.

    Returns True on success.
    """
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        print(f"ERROR: Skill not found: {skill_name}")
        return False

    # Validate
    errors = validate_skill(skill_dir)
    if errors:
        print(f"VALIDATION FAILED for {skill_name}:")
        for e in errors:
            print(f"  - {e}")
        return False

    # Assemble
    assembler = Assembler(CORE_DIR)
    assembled_content = assembler.assemble(journal, skill_dir)

    # Write to temp dir for adapter
    temp_skill_dir = output_dir / "_temp" / skill_name
    if temp_skill_dir.exists():
        shutil.rmtree(temp_skill_dir)
    shutil.copytree(skill_dir, temp_skill_dir)

    # Overwrite SKILL.md with assembled content
    (temp_skill_dir / "SKILL.md").write_text(assembled_content, encoding="utf-8")

    # Adapt
    adapter_cls = ADAPTERS.get(platform)
    if not adapter_cls:
        print(f"ERROR: Unknown platform: {platform}")
        return False

    adapter = adapter_cls()
    platform_output = output_dir / platform / journal
    platform_output.mkdir(parents=True, exist_ok=True)
    adapter.adapt_skill(temp_skill_dir, platform_output)

    # Cleanup temp
    shutil.rmtree(temp_skill_dir)

    print(f"OK: {skill_name} → {platform}/{journal}/")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build sci-craft skills")
    parser.add_argument("--journal", required=True, choices=["nature", "science"], help="Target journal")
    parser.add_argument("--platform", required=True, choices=["trae"], help="Target platform")
    parser.add_argument("--skill", default=None, help="Build a single skill (default: all)")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, do not build")
    args = parser.parse_args()

    if args.validate_only:
        skills = [args.skill] if args.skill else BUILTIN_SKILLS
        all_valid = True
        for name in skills:
            skill_dir = SKILLS_DIR / name
            errors = validate_skill(skill_dir)
            if errors:
                print(f"FAIL: {name}")
                for e in errors:
                    print(f"  - {e}")
                all_valid = False
            else:
                print(f"PASS: {name}")
        sys.exit(0 if all_valid else 1)

    skills = [args.skill] if args.skill else BUILTIN_SKILLS
    success = True
    for name in skills:
        if not build_skill(name, args.journal, args.platform, OUTPUT_DIR):
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
