"""Workflow orchestration engine."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class StepDef:
    """Workflow step definition."""

    id: str
    skill: str
    journal: str
    platform: str = "trae"
    depends_on: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)


@dataclass
class WorkflowDef:
    """Workflow definition."""

    name: str
    description: str = ""
    steps: list[StepDef] = field(default_factory=list)


@dataclass
class StepResult:
    """Result of a workflow step execution."""

    step_id: str
    success: bool
    output: str = ""
    error: str = ""


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_name: str
    success: bool
    step_results: list[StepResult] = field(default_factory=list)
    error: str = ""


class WorkflowEngine:
    """Workflow execution engine."""

    def __init__(self, workflows_dir: Path, skills_dir: Path):
        """Initialize workflow engine.

        Args:
            workflows_dir: Path to workflows directory
            skills_dir: Path to skills directory
        """
        self.workflows_dir = workflows_dir
        self.skills_dir = skills_dir

    def load_workflow(self, workflow_name: str) -> WorkflowDef:
        """Load workflow definition from YAML file.

        Args:
            workflow_name: Name of workflow (without .yaml extension)

        Returns:
            WorkflowDef object

        Raises:
            FileNotFoundError: If workflow file doesn't exist
            ValueError: If workflow is invalid
        """
        workflow_path = self.workflows_dir / f"{workflow_name}.yaml"

        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        with open(workflow_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        steps = []
        for step_data in data.get("steps", []):
            step = StepDef(
                id=step_data["id"],
                skill=step_data["skill"],
                journal=step_data.get("journal", "nature"),
                platform=step_data.get("platform", "trae"),
                depends_on=step_data.get("depends_on", []),
                config=step_data.get("config", {}),
            )
            steps.append(step)

        return WorkflowDef(
            name=data.get("name", workflow_name),
            description=data.get("description", ""),
            steps=steps,
        )

    def validate_workflow(self, workflow_def: WorkflowDef) -> list[str]:
        """Validate workflow definition.

        Checks:
        - All referenced skills exist
        - No circular dependencies
        - All dependencies reference existing steps

        Args:
            workflow_def: Workflow definition

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        step_ids = {step.id for step in workflow_def.steps}

        # Check all skills exist
        for step in workflow_def.steps:
            skill_path = self.skills_dir / step.skill
            if not skill_path.exists():
                errors.append(f"Step '{step.id}': Skill not found: {step.skill}")

        # Check dependencies reference existing steps
        for step in workflow_def.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.id}': Dependency not found: {dep}")

        # Check for cycles
        cycle = self._detect_cycle(workflow_def.steps)
        if cycle:
            errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

        return errors

    def _detect_cycle(self, steps: list[StepDef]) -> Optional[list[str]]:
        """Detect circular dependencies in workflow steps.

        Args:
            steps: List of step definitions

        Returns:
            Cycle path if found, None otherwise
        """
        # Build adjacency list
        graph = {step.id: step.depends_on for step in steps}

        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> Optional[list[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for step_id in graph:
            if step_id not in visited:
                cycle = dfs(step_id)
                if cycle:
                    return cycle

        return None

    def resolve_dependencies(self, steps: list[StepDef]) -> list[list[str]]:
        """Resolve step dependencies and return execution order.

        Uses topological sort to determine the order in which steps
        can be executed. Returns groups of steps that can be executed
        in parallel.

        Args:
            steps: List of step definitions

        Returns:
            List of step groups (each group can be executed in parallel)
        """
        # Build dependency graph
        in_degree = {step.id: 0 for step in steps}

        for step in steps:
            for dep in step.depends_on:
                if dep in in_degree:
                    in_degree[step.id] += 1

        # Find all nodes with no dependencies
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Current level - all nodes with in_degree 0
            level = queue[:]
            result.append(level)

            next_queue = []
            for node in level:
                # For each step that depends on this one
                for step in steps:
                    if node in step.depends_on:
                        in_degree[step.id] -= 1
                        if in_degree[step.id] == 0:
                            next_queue.append(step.id)

            queue = next_queue

        return result

    def execute(self, workflow_def: WorkflowDef, dry_run: bool = False) -> WorkflowResult:
        """Execute workflow.

        Args:
            workflow_def: Workflow definition
            dry_run: If True, only validate and plan, don't execute

        Returns:
            WorkflowResult with execution details
        """
        # Validate workflow
        errors = self.validate_workflow(workflow_def)
        if errors:
            return WorkflowResult(
                workflow_name=workflow_def.name,
                success=False,
                error="; ".join(errors),
            )

        # Resolve dependencies
        execution_order = self.resolve_dependencies(workflow_def.steps)

        step_results = []

        for level, step_ids in enumerate(execution_order):
            for step_id in step_ids:
                step = next(s for s in workflow_def.steps if s.id == step_id)

                if dry_run:
                    # Dry run - just record the step would execute
                    step_results.append(
                        StepResult(
                            step_id=step_id,
                            success=True,
                            output="[DRY RUN] Would execute skill: {step.skill}",
                        )
                    )
                else:
                    # Actual execution - this would call the skill
                    # For now, return a placeholder
                    step_results.append(
                        StepResult(
                            step_id=step_id,
                            success=True,
                            output=f"Executed skill: {step.skill} for journal: {step.journal}",
                        )
                    )

        return WorkflowResult(
            workflow_name=workflow_def.name,
            success=True,
            step_results=step_results,
        )
