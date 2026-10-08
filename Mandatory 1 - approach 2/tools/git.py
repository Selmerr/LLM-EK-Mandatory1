import subprocess
from pathlib import Path


class GitTools:

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)

    def run_git(self, *args):
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Git command failed:\n{result.stderr}"
            )

        return result.stdout.strip()

    def current_branch(self):
        return self.run_git(
            "branch",
            "--show-current"
        )

    def status(self):
        return self.run_git(
            "status",
            "--short"
        )

    def diff(self):
        return self.run_git(
            "diff"
        )

    def create_branch(self, branch_name):
        return self.run_git(
            "branch",
            branch_name
        )

    def switch_branch(self, branch_name):
        return self.run_git(
            "switch",
            branch_name
        )

    def commit(self, message):
        self.run_git("add", ".")
        return self.run_git(
            "commit",
            "-m",
            message
        )