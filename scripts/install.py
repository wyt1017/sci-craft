"""Install script — copy built skills to the target platform's skill directory."""
import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "output"

from adapters.trae import TraeAdapter

ADAPTERS = {
    "trae": TraeAdapter,
}


def install(journal: str, platform: str, skill: str | None = None) -> bool:
    """Install built skills to the platform's skill directory.

    Returns True on success.
    """
    adapter_cls = ADAPTERS.get(platform)
    if not adapter_cls:
        print(f"ERROR: Unknown platform: {platform}")
        return False

    adapter = adapter_cls()
    install_path = adapter.get_install_path()

    source_dir = OUTPUT_DIR / platform / journal
    if not source_dir.exists():
        print(f"ERROR: No built output found at {source_dir}. Run build first.")
        return False

    # Determine which skills to install
    if skill:
        skill_dirs = [source_dir / skill]
        if not skill_dirs[0].exists():
            print(f"ERROR: Skill not found in output: {skill}")
            return False
    else:
        skill_dirs = [d for d in source_dir.iterdir() if d.is_dir()]

    # Install
    install_path.mkdir(parents=True, exist_ok=True)

    for src in skill_dirs:
        dest = install_path / src.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"INSTALLED: {src.name} → {dest}")

    # Also install _shared if it exists
    shared_source = PROJECT_ROOT / "skills" / "_shared"
    if shared_source.exists():
        shared_dest = install_path / "_shared"
        if shared_dest.exists():
            shutil.rmtree(shared_dest)
        shutil.copytree(shared_source, shared_dest)
        print(f"INSTALLED: _shared → {shared_dest}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Install sci-craft skills to target platform")
    parser.add_argument("--journal", required=True, choices=["nature", "science"], help="Target journal")
    parser.add_argument("--platform", required=True, choices=["trae"], help="Target platform")
    parser.add_argument("--skill", default=None, help="Install a single skill (default: all)")
    args = parser.parse_args()

    success = install(args.journal, args.platform, args.skill)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
