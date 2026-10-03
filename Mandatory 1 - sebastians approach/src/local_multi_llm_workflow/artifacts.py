from __future__ import annotations

from pathlib import Path


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        return path

    def read_optional(self, relative_path: str) -> str:
        path = self.root / relative_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")
