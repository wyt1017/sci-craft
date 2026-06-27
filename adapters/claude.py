"""Claude Code platform adapter."""
import logging
import shutil
from pathlib import Path

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class ClaudeAdapter(BaseAdapter):
    """Adapter for Claude Code skill format.

    Claude Code uses:
    - CLAUDE.md as the instruction file (renamed from SKILL.md)
    - No manifest.yaml
    - Shared resources inlined into CLAUDE.md
    - Installed in project root directory
    """

    @property
    def platform_name(self) -> str:
        return "claude"

    def adapt_skill(self, skill_dir: Path, output_dir: Path) -> None:
        """Convert skill to Claude Code format."""
        skill_name = skill_dir.name
        dest = output_dir / skill_name

        try:
            shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to copy skill '{skill_name}' to {dest}: {e}")
            raise

        # Rename SKILL.md → CLAUDE.md
        skill_md = dest / "SKILL.md"
        claude_md = dest / "CLAUDE.md"
        if skill_md.exists():
            try:
                shutil.move(skill_md, claude_md)
            except Exception as e:
                logger.warning(f"Failed to rename SKILL.md to CLAUDE.md in '{skill_name}': {e}")

        # Remove manifest.yaml (Claude Code doesn't use it)
        manifest = dest / "manifest.yaml"
        if manifest.exists():
            try:
                manifest.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove manifest.yaml from '{skill_name}': {e}")

        # Inline shared resources if they exist
        # _shared is placed alongside the skill in output/_temp/ by build.py
        shared_dir = skill_dir.parent / "_shared"
        if shared_dir.exists() and claude_md.exists():
            try:
                shared_content = self._read_shared(shared_dir)
                if shared_content:
                    current = claude_md.read_text(encoding="utf-8")
                    claude_md.write_text(
                        current + "\n\n---\n\n# Shared Resources\n\n" + shared_content,
                        encoding="utf-8",
                    )
            except Exception as e:
                logger.warning(f"Failed to inline shared resources for '{skill_name}': {e}")

    def _read_shared(self, shared_dir: Path) -> str:
        """Read and concatenate all .md files from _shared/."""
        parts: list[str] = []
        for md_file in sorted(shared_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            if content.strip():
                parts.append(f"## {md_file.stem}\n\n{content}")
        return "\n\n".join(parts)

    def get_install_path(self) -> Path:
        """Return current working directory (Claude Code uses project root)."""
        return Path.cwd()
