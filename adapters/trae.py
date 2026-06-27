"""TRAE platform adapter."""
import logging
import shutil
from pathlib import Path

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class TraeAdapter(BaseAdapter):
    """Adapter for TRAE IDE skill format.

    TRAE uses:
    - SKILL.md as the instruction file
    - manifest.yaml for metadata and triggers
    - references/ for supplementary rule files
    - skills/_shared/ for shared resources
    """

    @property
    def platform_name(self) -> str:
        return "trae"

    def adapt_skill(self, skill_dir: Path, output_dir: Path) -> None:
        """Copy skill directory to output, preserving structure for TRAE.

        TRAE uses the same format as our source skills, so this is
        primarily a directory copy operation.
        """
        skill_name = skill_dir.name
        dest = output_dir / skill_name

        try:
            shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to copy skill '{skill_name}' to {dest}: {e}")
            raise

    def get_install_path(self) -> Path:
        """Return TRAE skills directory path."""
        return Path.home() / ".trae" / "skills"
