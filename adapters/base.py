"""Base adapter interface for multi-platform skill conversion."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseAdapter(ABC):
    """Abstract base class for platform adapters."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Unique platform identifier."""
        ...

    @abstractmethod
    def adapt_skill(self, skill_dir: Path, output_dir: Path) -> None:
        """Convert a skill directory to the target platform format.

        Args:
            skill_dir: Source skill directory.
            output_dir: Destination directory for adapted output.
        """
        ...

    @abstractmethod
    def get_install_path(self) -> Path:
        """Return the default skill installation path for this platform."""
        ...
