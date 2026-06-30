"""Tests for engine/workflow.py - Workflow orchestration."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from engine.workflow import StepDef, WorkflowDef, WorkflowEngine


def test_step_def():
    """Test StepDef dataclass."""
    step = StepDef(
        id="step1",
        skill="literature-search",
        journal="nature",
        platform="trae",
        depends_on=["step0"],
        config={"query": "test"},
    )

    assert step.id == "step1"
    assert step.skill == "literature-search"
    assert step.depends_on == ["step0"]


def test_workflow_def():
    """Test WorkflowDef dataclass."""
    steps = [
        StepDef(id="s1", skill="skill1", journal="nature"),
        StepDef(id="s2", skill="skill2", journal="nature", depends_on=["s1"]),
    ]

    workflow = WorkflowDef(
        name="test-workflow",
        description="Test workflow",
        steps=steps,
    )

    assert workflow.name == "test-workflow"
    assert len(workflow.steps) == 2


def test_workflow_engine_init():
    """Test WorkflowEngine initialization."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        engine = WorkflowEngine(workflows_dir, skills_dir)
        assert engine.workflows_dir == workflows_dir
        assert engine.skills_dir == skills_dir


def test_load_workflow():
    """Test loading workflow from YAML."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        # Create workflow YAML
        workflow_data = {
            "name": "test-workflow",
            "description": "Test description",
            "steps": [
                {
                    "id": "step1",
                    "skill": "skill1",
                    "journal": "nature",
                    "platform": "trae",
                },
                {
                    "id": "step2",
                    "skill": "skill2",
                    "journal": "nature",
                    "depends_on": ["step1"],
                    "config": {"key": "value"},
                },
            ],
        }
        with open(workflows_dir / "test-workflow.yaml", "w") as f:
            yaml.dump(workflow_data, f)

        engine = WorkflowEngine(workflows_dir, skills_dir)
        workflow = engine.load_workflow("test-workflow")

        assert workflow.name == "test-workflow"
        assert workflow.description == "Test description"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].id == "step1"
        assert workflow.steps[1].depends_on == ["step1"]


def test_load_workflow_not_found():
    """Test loading workflow that doesn't exist."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        engine = WorkflowEngine(workflows_dir, skills_dir)

        with pytest.raises(FileNotFoundError):
            engine.load_workflow("nonexistent")


def test_validate_workflow_missing_skill():
    """Test workflow validation for missing skill."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        workflow = WorkflowDef(
            name="test",
            steps=[
                StepDef(id="s1", skill="nonexistent-skill", journal="nature"),
            ],
        )

        engine = WorkflowEngine(workflows_dir, skills_dir)
        errors = engine.validate_workflow(workflow)

        assert len(errors) > 0
        assert any("Skill not found" in e for e in errors)


def test_validate_workflow_missing_dependency():
    """Test workflow validation for missing dependency."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        # Create skill
        (skills_dir / "skill1").mkdir()

        workflow = WorkflowDef(
            name="test",
            steps=[
                StepDef(id="s1", skill="skill1", journal="nature", depends_on=["nonexistent"]),
            ],
        )

        engine = WorkflowEngine(workflows_dir, skills_dir)
        errors = engine.validate_workflow(workflow)

        assert any("Dependency not found" in e for e in errors)


def test_detect_cycle():
    """Test cycle detection in workflow."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        # Create skills
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill2").mkdir()
        (skills_dir / "skill3").mkdir()

        # Create cyclic workflow: s1 -> s2 -> s3 -> s1
        workflow = WorkflowDef(
            name="cyclic",
            steps=[
                StepDef(id="s1", skill="skill1", journal="nature", depends_on=["s3"]),
                StepDef(id="s2", skill="skill2", journal="nature", depends_on=["s1"]),
                StepDef(id="s3", skill="skill3", journal="nature", depends_on=["s2"]),
            ],
        )

        engine = WorkflowEngine(workflows_dir, skills_dir)
        cycle = engine._detect_cycle(workflow.steps)

        assert cycle is not None
        assert len(cycle) >= 3


def test_resolve_dependencies():
    """Test dependency resolution (topological sort)."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        steps = [
            StepDef(id="s1", skill="skill1", journal="nature"),
            StepDef(id="s2", skill="skill2", journal="nature", depends_on=["s1"]),
            StepDef(id="s3", skill="skill3", journal="nature", depends_on=["s1"]),
            StepDef(id="s4", skill="skill4", journal="nature", depends_on=["s2", "s3"]),
        ]

        engine = WorkflowEngine(workflows_dir, skills_dir)
        order = engine.resolve_dependencies(steps)

        # s1 should be in first level
        assert "s1" in order[0]

        # s2 and s3 should be in second level (after s1)
        assert "s2" in order[1] or "s3" in order[1]

        # s4 should be in later level (after s2 and s3)
        assert any("s4" in level for level in order[2:])


def test_execute_workflow_dry_run():
    """Test workflow execution in dry run mode."""
    with TemporaryDirectory() as tmpdir:
        workflows_dir = Path(tmpdir) / "workflows"
        skills_dir = Path(tmpdir) / "skills"
        workflows_dir.mkdir()
        skills_dir.mkdir()

        # Create skills
        (skills_dir / "skill1").mkdir()
        (skills_dir / "skill2").mkdir()

        workflow = WorkflowDef(
            name="test",
            steps=[
                StepDef(id="s1", skill="skill1", journal="nature"),
                StepDef(id="s2", skill="skill2", journal="nature", depends_on=["s1"]),
            ],
        )

        engine = WorkflowEngine(workflows_dir, skills_dir)
        result = engine.execute(workflow, dry_run=True)

        assert result.success is True
        assert len(result.step_results) == 2
