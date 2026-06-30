"""Workflow command for sci-craft CLI."""

import argparse
from pathlib import Path

from engine.workflow import WorkflowEngine


def find_project_root() -> Path:
    """Find project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "skills").exists() and (current / "core").exists():
            return current
        current = current.parent
    return Path.cwd()


def list_workflows(project_dir: Path) -> list[str]:
    """List available workflows."""
    workflows_dir = project_dir / "core" / "workflows"
    if not workflows_dir.exists():
        return []

    workflows = []
    for yaml_file in workflows_dir.glob("*.yaml"):
        workflows.append(yaml_file.stem)
    return workflows


def run_workflow(workflow_name: str, project_dir: Path, dry_run: bool = False) -> bool:
    """Run a workflow.

    Args:
        workflow_name: Workflow name
        project_dir: Project root directory
        dry_run: Dry run mode

    Returns:
        True if workflow succeeded, False otherwise
    """
    workflows_dir = project_dir / "core" / "workflows"
    skills_dir = project_dir / "skills"

    engine = WorkflowEngine(workflows_dir, skills_dir)

    try:
        workflow_def = engine.load_workflow(workflow_name)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False

    print(f"Workflow: {workflow_def.name}")
    print(f"Description: {workflow_def.description}")
    print(f"Steps: {len(workflow_def.steps)}")

    # Validate workflow
    errors = engine.validate_workflow(workflow_def)
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    # Resolve dependencies
    execution_order = engine.resolve_dependencies(workflow_def.steps)
    print("\nExecution order:")
    for level, step_ids in enumerate(execution_order):
        print(f"  Level {level}: {step_ids}")

    if dry_run:
        print("\n[DRY RUN] Workflow validated successfully")
        return True

    # Execute workflow
    result = engine.execute(workflow_def, dry_run=False)
    if result.success:
        print("\n✓ Workflow executed successfully")
        for step_result in result.step_results:
            print(f"  - {step_result.step_id}: {step_result.output}")
        return True
    else:
        print(f"\n✗ Workflow failed: {result.error}")
        return False


def main():
    """Main entry point for workflow command."""
    parser = argparse.ArgumentParser(description="Manage sci-craft workflows")
    parser.add_argument(
        "action",
        choices=["list", "run", "validate"],
        help="Workflow action",
    )
    parser.add_argument(
        "--name",
        "-n",
        help="Workflow name (for run/validate)",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Dry run mode (validate only)",
    )

    args = parser.parse_args()

    project_dir = find_project_root()

    if args.action == "list":
        workflows = list_workflows(project_dir)
        print("Available workflows:")
        for workflow in workflows:
            print(f"  - {workflow}")
        if not workflows:
            print("  (No workflows found)")
        return 0

    elif args.action == "run":
        if not args.name:
            print("ERROR: Workflow name required for run")
            return 1

        success = run_workflow(args.name, project_dir, args.dry_run)
        return 0 if success else 1

    elif args.action == "validate":
        if not args.name:
            print("ERROR: Workflow name required for validate")
            return 1

        success = run_workflow(args.name, project_dir, dry_run=True)
        return 0 if success else 1


if __name__ == "__main__":
    exit(main())