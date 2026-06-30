"""Build script — assemble and validate skills for a target journal and platform."""

import argparse
import logging
import shutil
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# isort: off
from adapters.trae import TraeAdapter
from adapters.codex import CodexAdapter
from adapters.claude import ClaudeAdapter
from builder.assembler import Assembler
from builder.validator import validate_skill
# isort: on

logger = logging.getLogger(__name__)

SKILLS_DIR = PROJECT_ROOT / "skills"
CORE_DIR = PROJECT_ROOT / "core"
OUTPUT_DIR = PROJECT_ROOT / "output"

ADAPTERS = {
    "trae": TraeAdapter,
    "codex": CodexAdapter,
    "claude": ClaudeAdapter,
}

BUILTIN_SKILLS = [
    d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != "_shared" and (d / "manifest.yaml").exists()
]


def build_skill(skill_name: str, journal: str, platform: str, output_dir: Path) -> bool:
    """Build a single skill for a specific journal and platform.

    Uses a temporary directory for atomic operations — only moves to final
    location on success.

    Returns True on success.
    """
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        logger.error("Skill not found: %s", skill_name)
        return False

    # Validate
    errors = validate_skill(skill_dir)
    if errors:
        logger.error("VALIDATION FAILED for %s:", skill_name)
        for e in errors:
            logger.error("  - %s", e)
        return False

    # Assemble
    assembler = Assembler(CORE_DIR)
    assembled_content = assembler.assemble(journal, skill_dir)

    # Write to temp dir for atomic operation
    temp_base = output_dir / "_temp"
    temp_base.mkdir(parents=True, exist_ok=True)
    temp_skill_dir = tempfile.mkdtemp(dir=str(temp_base), prefix=f"{skill_name}-")
    temp_skill_dir = Path(temp_skill_dir)

    try:
        # Copy skill to temp dir (mkdtemp creates empty dir, copytree expects non-existent dst or empty dst)
        shutil.copytree(skill_dir, temp_skill_dir, dirs_exist_ok=True)

        # Also copy _shared for adapters that need it (e.g., Claude)
        shared_source = SKILLS_DIR / "_shared"
        if shared_source.exists():
            shared_dest = temp_skill_dir.parent / "_shared"
            shutil.copytree(shared_source, shared_dest, dirs_exist_ok=True)

        # Overwrite SKILL.md with assembled content
        (temp_skill_dir / "SKILL.md").write_text(assembled_content, encoding="utf-8")

        # Adapt
        adapter_cls = ADAPTERS.get(platform)
        if not adapter_cls:
            logger.error("Unknown platform: %s", platform)
            return False

        adapter = adapter_cls()
        platform_output = output_dir / platform / journal
        platform_output.mkdir(parents=True, exist_ok=True)
        adapter.adapt_skill(temp_skill_dir, platform_output)
        logger.info("Built: %s → %s/%s/", skill_name, platform, journal)
        return True

    finally:
        # Always cleanup temp dir
        shutil.rmtree(temp_skill_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Build sci-craft skills")
    parser.add_argument("--journal", choices=["nature", "science"], help="Target journal (required for build)")
    parser.add_argument("--platform", choices=["trae", "codex", "claude"], help="Target platform (required for build)")
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
                logger.error("FAIL: %s", name)
                for e in errors:
                    logger.error("  - %s", e)
                all_valid = False
            else:
                logger.info("PASS: %s", name)
        sys.exit(0 if all_valid else 1)

    # Build mode requires journal and platform
    if not args.journal or not args.platform:
        parser.error("--journal and --platform are required for build mode (use --validate-only to skip)")

    skills = [args.skill] if args.skill else BUILTIN_SKILLS
    success = True
    for name in skills:
        if not build_skill(name, args.journal, args.platform, OUTPUT_DIR):
            success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
