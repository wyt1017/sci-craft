"""Tests for CLI module."""

import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestCliInit:
    """Tests for cli/__init__.py."""

    def test_cli_exports_build(self):
        """Test that build module is exported."""
        from cli import build

        assert build is not None

    def test_cli_exports_workflow(self):
        """Test that workflow module is exported."""
        from cli import workflow

        assert workflow is not None

    def test_cli_exports_validate(self):
        """Test that validate module is exported."""
        from cli import validate

        assert validate is not None

    def test_cli_exports_cache(self):
        """Test that cache module is exported."""
        from cli import cache

        assert cache is not None

    def test_cli_all_exports(self):
        """Test that all expected modules are in __all__."""
        from cli import __all__

        assert "build" in __all__
        assert "workflow" in __all__
        assert "validate" in __all__
        assert "cache" in __all__
