"""Install script — copy built skills to the target platform's skill directory."""

import argparse
import logging
import shutil
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "output"

# isort: off
from adapters.trae import TraeAdapter
from adapters.codex import CodexAdapter
from adapters.claude import ClaudeAdapter
# isort: on

ADAPTERS = {
    "trae": TraeAdapter,
    "codex": CodexAdapter,
    "claude": ClaudeAdapter,
}


def install(journal: str, platform: str, skill: str | None = None, force: bool = False) -> bool:
    """Install built skills to the platform's skill directory.

    Args:
        journal: Target journal name.
        platform: Target platform name.
        skill: Specific skill to install (None for all).
        force: If True, overwrite existing skills without warning.

    Returns True on success.
    """
    adapter_cls = ADAPTERS.get(platform)
    if not adapter_cls:
        logger.error("Unknown platform: %s", platform)
        return False

    adapter = adapter_cls()
    install_path = adapter.get_install_path()

    source_dir = OUTPUT_DIR / platform / journal
    if not source_dir.exists():
        logger.error("No built output found at %s. Run build first.", source_dir)
        return False

    # Determine which skills to install
    if skill:
        skill_dirs = [source_dir / skill]
        if not skill_dirs[0].exists():
            logger.error("Skill not found in output: %s", skill)
            return False
    else:
        skill_dirs = [d for d in source_dir.iterdir() if d.is_dir()]

    # Install
    install_path.mkdir(parents=True, exist_ok=True)

    for src in skill_dirs:
        dest = install_path / src.name
        if dest.exists():
            if force:
                shutil.rmtree(dest)
                shutil.copytree(src, dest)
                logger.info("Overridden: %s → %s", src.name, dest)
            else:
                logger.info("Skipped: %s (already exists, use --force to overwrite)", src.name)
        else:
            shutil.copytree(src, dest)
            logger.info("Installed: %s → %s", src.name, dest)

    # Also install _shared if it exists
    shared_source = PROJECT_ROOT / "skills" / "_shared"
    if shared_source.exists():
        shared_dest = install_path / "_shared"
        if shared_dest.exists():
            if force:
                shutil.rmtree(shared_dest)
                shutil.copytree(shared_source, shared_dest)
                logger.info("Overridden: _shared → %s", shared_dest)
            else:
                logger.info("Skipped: _shared (already exists, use --force to overwrite)")
        else:
            shutil.copytree(shared_source, shared_dest)
            logger.info("Installed: _shared → %s", shared_dest)

    return True


def main():
    parser = argparse.ArgumentParser(description="Install sci-craft skills to target platform")
    parser.add_argument("--journal", required=True, choices=["nature", "science"], help="Target journal")
    parser.add_argument("--platform", required=True, choices=["trae", "codex", "claude"], help="Target platform")
    parser.add_argument("--skill", default=None, help="Install a single skill (default: all)")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing installations")
    args = parser.parse_args()

    success = install(args.journal, args.platform, args.skill, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
