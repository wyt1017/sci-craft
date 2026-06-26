"""Claude Code platform adapter."""
import shutil
from pathlib import Path

from adapters.base import BaseAdapter


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

        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(skill_dir, dest)

        # Rename SKILL.md → CLAUDE.md
        skill_md = dest / "SKILL.md"
        claude_md = dest / "CLAUDE.md"
        if skill_md.exists():
            shutil.move(str(skill_md), str(claude_md))

        # Remove manifest.yaml (Claude Code doesn't use it)
        manifest = dest / "manifest.yaml"
        if manifest.exists():
            manifest.unlink()

        # Inline shared resources if they exist
        shared_dir = skill_dir.parent / "_shared"
        if shared_dir.exists() and claude_md.exists():
            shared_content = self._read_shared(shared_dir)
            if shared_content:
                current = claude_md.read_text(encoding="utf-8")
                claude_md.write_text(
                    current + "\n\n---\n\n# Shared Resources\n\n" + shared_content,
                    encoding="utf-8",
                )

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
