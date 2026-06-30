"""Tests for engine/cache.py - Dependency-level caching."""

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml

from engine.cache import DependencyCache, DepNode


def test_dep_node():
    """Test DepNode dataclass."""
    node = DepNode(
        manifest_hash="abc123",
        skill_md_hash="def456",
        rules_hashes=["hash1", "hash2"],
        references_hashes=["ref1"],
        journal_config_hash="ghi789",
    )

    assert node.manifest_hash == "abc123"
    assert len(node.rules_hashes) == 2


def test_dependency_cache_init():
    """Test DependencyCache initialization."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        assert cache.project_dir == project_dir
        assert cache.cache_path == project_dir / ".sci_craft_cache.json"


def test_dependency_cache_empty():
    """Test empty cache initialization."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        stats = cache.get_cache_stats()
        assert stats["total_skills"] == 0
        assert stats["total_cached_builds"] == 0


def test_compute_file_hash():
    """Test file hash computation."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        test_file = project_dir / "test.txt"
        test_file.write_text("test content")

        cache = DependencyCache(project_dir)
        hash_val = cache._compute_file_hash(test_file)

        # Verify it's a valid MD5 hash
        assert len(hash_val) == 32
        expected = hashlib.md5(b"test content").hexdigest()
        assert hash_val == expected


def test_compute_file_hash_missing():
    """Test hash computation for missing file."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        hash_val = cache._compute_file_hash(project_dir / "nonexistent.txt")
        assert hash_val == ""


def test_compute_dependency_graph():
    """Test dependency graph computation."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        core_dir = project_dir / "core"
        skills_dir = project_dir / "skills"
        skill_dir = skills_dir / "test-skill"

        skill_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "journals").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules").mkdir(parents=True, exist_ok=True)
        (core_dir / "rules" / "writing").mkdir(parents=True, exist_ok=True)

        # Write skill files
        manifest = {
            "id": "test-skill",
            "name": "Test",
            "rules": ["writing/sentence-length.md"],
        }
        with open(skill_dir / "manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        with open(skill_dir / "SKILL.md", "w") as f:
            f.write("# Test Skill")

        with open(core_dir / "rules" / "writing" / "sentence-length.md", "w") as f:
            f.write("# Sentence Length")

        with open(core_dir / "journals" / "nature.yaml", "w") as f:
            yaml.dump({"name": "nature"}, f)

        cache = DependencyCache(project_dir)
        dep_node = cache.compute_dependency_graph(
            skill_dir=skill_dir,
            journal="nature",
            journals_dir=core_dir / "journals",
            rules_dir=core_dir / "rules",
        )

        assert dep_node.manifest_hash != ""
        assert dep_node.skill_md_hash != ""
        assert len(dep_node.rules_hashes) == 1


def test_should_rebuild_new_skill():
    """Test rebuild decision for new skill."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        dep_node = DepNode(
            manifest_hash="abc",
            skill_md_hash="def",
            rules_hashes=[],
            references_hashes=[],
            journal_config_hash="ghi",
        )

        # New skill should always need rebuild
        assert cache.should_rebuild("new-skill", "nature", dep_node) is True


def test_update_and_check_cache():
    """Test cache update and rebuild check."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        dep_node = DepNode(
            manifest_hash="abc",
            skill_md_hash="def",
            rules_hashes=["rule1"],
            references_hashes=["ref1"],
            journal_config_hash="ghi",
        )

        # Update cache
        cache.update_cache("test-skill", "nature", dep_node)

        # Same hash should not need rebuild
        assert cache.should_rebuild("test-skill", "nature", dep_node) is False

        # Different hash should need rebuild
        new_node = DepNode(
            manifest_hash="xyz",  # Different
            skill_md_hash="def",
            rules_hashes=["rule1"],
            references_hashes=["ref1"],
            journal_config_hash="ghi",
        )
        assert cache.should_rebuild("test-skill", "nature", new_node) is True


def test_clear_cache():
    """Test cache clearing."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        # Add some cache entries
        dep_node = DepNode(
            manifest_hash="abc",
            skill_md_hash="def",
            rules_hashes=[],
            references_hashes=[],
            journal_config_hash="ghi",
        )
        cache.update_cache("skill1", "nature", dep_node)
        cache.update_cache("skill2", "nature", dep_node)

        # Clear cache
        cache.clear_cache()

        stats = cache.get_cache_stats()
        assert stats["total_skills"] == 0


def test_get_cached_skills():
    """Test getting cached skill names."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        dep_node = DepNode(
            manifest_hash="abc",
            skill_md_hash="def",
            rules_hashes=[],
            references_hashes=[],
            journal_config_hash="ghi",
        )

        cache.update_cache("skill-a", "nature", dep_node)
        cache.update_cache("skill-b", "science", dep_node)

        skills = cache.get_cached_skills()
        assert "skill-a" in skills
        assert "skill-b" in skills


def test_cache_file_created():
    """Test that cache file is created on disk."""
    with TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        cache = DependencyCache(project_dir)

        dep_node = DepNode(
            manifest_hash="abc",
            skill_md_hash="def",
            rules_hashes=[],
            references_hashes=[],
            journal_config_hash="ghi",
        )

        cache.update_cache("test-skill", "nature", dep_node)

        # Cache file should exist
        assert cache.cache_path.exists()