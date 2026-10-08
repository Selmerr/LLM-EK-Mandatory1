from pathlib import Path


class FileTools:

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path).resolve()

    def _safe_path(self, relative_path):
        path = (self.repo_path / relative_path).resolve()

        if not path.is_relative_to(self.repo_path):
            raise ValueError(
                f"Path is outside the repository: {relative_path}"
            )

        return path

    def read(self, relative_path):
        path = self._safe_path(relative_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File does not exist: {relative_path}"
            )

        return path.read_text(encoding="utf-8")

    def write(self, relative_path, content):
        path = self._safe_path(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

    def exists(self, relative_path):
        return self._safe_path(relative_path).exists()