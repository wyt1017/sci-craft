"""Cache command for sci-craft CLI."""

import argparse
from pathlib import Path

from engine.cache import DependencyCache


def find_project_root() -> Path:
    """Find project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "skills").exists() and (current / "core").exists():
            return current
        current = current.parent
    return Path.cwd()


def show_cache_stats(project_dir: Path) -> None:
    """Show cache statistics."""
    cache = DependencyCache(project_dir)
    stats = cache.get_cache_stats()

    print("Cache Statistics:")
    print(f"  Cached skills: {stats['total_skills']}")
    print(f"  Total cached builds: {stats['total_cached_builds']}")
    print(f"  Cache file: {stats['cache_file']}")

    if stats["total_skills"] > 0:
        print("\nCached skills:")
        for skill_name in cache.get_cached_skills():
            print(f"  - {skill_name}")


def clear_cache(project_dir: Path) -> None:
    """Clear the cache."""
    cache = DependencyCache(project_dir)
    cache.clear_cache()
    print("Cache cleared successfully")


def main():
    """Main entry point for cache command."""
    parser = argparse.ArgumentParser(description="Manage sci-craft cache")
    parser.add_argument(
        "action",
        choices=["stats", "clear", "list"],
        help="Cache action",
    )

    args = parser.parse_args()

    project_dir = find_project_root()

    if args.action == "stats":
        show_cache_stats(project_dir)
    elif args.action == "clear":
        clear_cache(project_dir)
    elif args.action == "list":
        cache = DependencyCache(project_dir)
        skills = cache.get_cached_skills()
        if skills:
            print("Cached skills:")
            for skill in skills:
                print(f"  - {skill}")
        else:
            print("No cached skills")

    return 0


if __name__ == "__main__":
    exit(main())
