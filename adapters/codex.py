"""Codex platform adapter."""
import shutil
from pathlib import Path

from adapters.base import BaseAdapter


class CodexAdapter(BaseAdapter):
    """Adapter for OpenAI Codex skill format.

    Codex uses:
    - SKILL.md as the instruction file
    - No manifest.yaml (not used by Codex)
    - skills/_shared/ for shared resources
    """

    @property
    def platform_name(self) -> str:
        return "codex"

    def adapt_skill(self, skill_dir: Path, output_dir: Path) -> None:
        """Copy skill directory to output, excluding manifest.yaml for Codex."""
        skill_name = skill_dir.name
        dest = output_dir / skill_name

        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(skill_dir, dest)

        # Remove manifest.yaml (Codex doesn't use it)
        manifest = dest / "manifest.yaml"
        if manifest.exists():
            manifest.unlink()

    def get_install_path(self) -> Path:
        """Return Codex skills directory path."""
        return Path.home() / ".codex" / "skills"
