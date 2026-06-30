"""CLI main entry point for python -m cli execution."""

import sys


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m cli <command> [options]")
        print("Commands: build, workflow, validate, cache")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "build":
        from cli.build import main as build_main
        sys.argv = ["build"] + args
        return build_main()
    elif command == "workflow":
        from cli.workflow import main as workflow_main
        sys.argv = ["workflow"] + args
        return workflow_main()
    elif command == "validate":
        from cli.validate import main as validate_main
        sys.argv = ["validate"] + args
        return validate_main()
    elif command == "cache":
        from cli.cache import main as cache_main
        sys.argv = ["cache"] + args
        return cache_main()
    else:
        print(f"Unknown command: {command}")
        print("Commands: build, workflow, validate, cache")
        return 1


if __name__ == "__main__":
    sys.exit(main())
