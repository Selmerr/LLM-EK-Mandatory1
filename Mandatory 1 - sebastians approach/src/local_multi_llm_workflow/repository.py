from __future__ import annotations

import difflib
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path


_INPUT_LOCK = threading.Lock()


@dataclass(frozen=True)
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class FileBlock:
    path: str
    content: str


class Repository:
    def __init__(self, root: Path, ask_before_commands: bool, ask_before_file_edits: bool) -> None:
        self.root = root
        self.ask_before_commands = ask_before_commands
        self.ask_before_file_edits = ask_before_file_edits

    def tree(self) -> str:
        lines: list[str] = []
        if not self.root.exists():
            return (
                f"(target repository directory {self.root.name}/ does not exist yet; "
                "implementation patches may create it by adding files under that path)"
            )
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not _is_ignored(path):
                lines.append(str(path.relative_to(self.root)).replace("\\", "/"))
        return "\n".join(lines) or "(target repository is empty)"

    def ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def write(self, relative_path: str, content: str) -> str:
        path = self.root / relative_path
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        diff = unified_diff(relative_path, old, content)
        if self.ask_before_file_edits and not _confirm(f"Apply edit to {relative_path}?"):
            return diff
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return diff

    def run(self, command: str) -> CommandResult:
        if self.ask_before_commands and not _confirm(f"Run command: {command}?"):
            return CommandResult(command=command, returncode=130, stdout="", stderr="Skipped by user")
        completed = subprocess.run(
            command,
            cwd=self.root.parent,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def apply_git_diff(self, diff_text: str) -> CommandResult:
        normalized_diff = _extract_unified_diff(diff_text)
        if not _looks_like_unified_diff(normalized_diff):
            return CommandResult(
                "git apply",
                2,
                "",
                "Model output was not a unified git diff, so no files were changed.",
            )
        invalid_paths = _paths_outside_root(normalized_diff, self.root.name)
        if invalid_paths:
            formatted = ", ".join(invalid_paths)
            return CommandResult(
                "git apply",
                3,
                "",
                f"Patch rejected because it modifies files outside {self.root.name}/: {formatted}",
            )
        if self.ask_before_file_edits and not _confirm(_approval_question(normalized_diff, self.root.name)):
            return CommandResult("git apply", 130, "", "Skipped by user")
        completed = subprocess.run(
            ["git", "apply", "--whitespace=fix"],
            cwd=self.root.parent,
            input=normalized_diff,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        return CommandResult("git apply --whitespace=fix", completed.returncode, completed.stdout, completed.stderr)

    def apply_file_blocks(self, blocks: list[FileBlock], source: str) -> CommandResult:
        if not blocks:
            return CommandResult(source, 2, "", "Model output did not contain any BEGIN_FILE blocks.")

        invalid_paths = [block.path for block in blocks if not _path_inside_root(block.path, self.root.name)]
        if invalid_paths:
            formatted = ", ".join(sorted(set(invalid_paths)))
            return CommandResult(
                source,
                3,
                "",
                f"File bundle rejected because it modifies files outside {self.root.name}/: {formatted}",
            )

        if self.ask_before_file_edits and not _confirm(_file_block_approval_question(blocks, self.root.name)):
            return CommandResult(source, 130, "", "Skipped by user")

        for block in blocks:
            target = self.root.parent / block.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(block.content.rstrip() + "\n", encoding="utf-8")

        return CommandResult(source, 0, f"Wrote {len(blocks)} file(s).", "")


def unified_diff(relative_path: str, old: str, new: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{relative_path}",
            tofile=f"b/{relative_path}",
        )
    )


def _confirm(question: str) -> bool:
    with _INPUT_LOCK:
        answer = input(f"{question} [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def _is_ignored(path: Path) -> bool:
    ignored_parts = {".git", "__pycache__", ".pytest_cache", ".venv", "artifacts"}
    return any(part in ignored_parts for part in path.parts)


def _looks_like_unified_diff(diff_text: str) -> bool:
    return (
        "diff --git " in diff_text
        or ("--- " in diff_text and "+++ " in diff_text and "@@" in diff_text)
    )


def _extract_unified_diff(diff_text: str) -> str:
    git_diff_start = diff_text.find("diff --git ")
    if git_diff_start >= 0:
        return diff_text[git_diff_start:].strip() + "\n"

    file_header_start = diff_text.find("--- ")
    if file_header_start >= 0:
        return diff_text[file_header_start:].strip() + "\n"

    return diff_text.strip() + "\n"


def _paths_outside_root(diff_text: str, root_name: str) -> list[str]:
    invalid: list[str] = []
    allowed_prefix = f"{root_name}/"
    for line in diff_text.splitlines():
        if not line.startswith("diff --git "):
            continue

        parts = line.split()
        if len(parts) < 4:
            invalid.append(line)
            continue

        for raw_path in parts[2:4]:
            path = _strip_git_prefix(raw_path)
            if path == "/dev/null":
                continue
            if not path.startswith(allowed_prefix):
                invalid.append(path)

    return sorted(set(invalid))


def _strip_git_prefix(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def _approval_question(diff_text: str, root_name: str) -> str:
    paths = _changed_paths(diff_text)
    folders = sorted(
        {
            str(Path(path).parent).replace("\\", "/")
            for path in paths
            if str(Path(path).parent).replace("\\", "/") not in {".", ""}
        }
    )

    path_preview = ", ".join(paths[:5]) if paths else "unknown files"
    if len(paths) > 5:
        path_preview += f", ... ({len(paths)} files total)"

    folder_preview = ", ".join(folders[:5]) if folders else root_name
    if len(folders) > 5:
        folder_preview += f", ... ({len(folders)} folders total)"

    return (
        "Apply model-generated git diff? "
        f"This may create/update files under {root_name}/. "
        f"Folders: {folder_preview}. Files: {path_preview}."
    )


def _changed_paths(diff_text: str) -> list[str]:
    paths: list[str] = []
    for line in diff_text.splitlines():
        if not line.startswith("diff --git "):
            continue
        parts = line.split()
        if len(parts) >= 4:
            path = _strip_git_prefix(parts[3])
            if path != "/dev/null":
                paths.append(path)
    return sorted(set(paths))


def parse_file_blocks(text: str) -> list[FileBlock]:
    blocks: list[FileBlock] = []
    current_path: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("BEGIN_FILE "):
            if current_path is not None:
                blocks.append(FileBlock(current_path, _clean_block_content(current_lines)))
            current_path = stripped.removeprefix("BEGIN_FILE ").strip()
            current_lines = []
            continue
        if stripped == "END_FILE" and current_path is not None:
            blocks.append(FileBlock(current_path, _clean_block_content(current_lines)))
            current_path = None
            current_lines = []
            continue
        if current_path is not None:
            current_lines.append(line)

    if current_path is not None:
        blocks.append(FileBlock(current_path, _clean_block_content(current_lines)))

    return blocks


def _clean_block_content(lines: list[str]) -> str:
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)


def _path_inside_root(path: str, root_name: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("/")
    if ".." in Path(normalized).parts:
        return False
    return normalized.startswith(f"{root_name}/")


def _file_block_approval_question(blocks: list[FileBlock], root_name: str) -> str:
    paths = sorted(block.path for block in blocks)
    folders = sorted(
        {
            str(Path(path).parent).replace("\\", "/")
            for path in paths
            if str(Path(path).parent).replace("\\", "/") not in {".", ""}
        }
    )
    path_preview = ", ".join(paths[:5])
    if len(paths) > 5:
        path_preview += f", ... ({len(paths)} files total)"
    folder_preview = ", ".join(folders[:5]) if folders else root_name
    if len(folders) > 5:
        folder_preview += f", ... ({len(folders)} folders total)"
    return (
        "Create/update generated files? "
        f"This may create folders under {root_name}/. "
        f"Folders: {folder_preview}. Files: {path_preview}."
    )
