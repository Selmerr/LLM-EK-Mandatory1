from pathlib import Path

from tools.git import GitTools
from tools.files import FileTools


class DeveloperWorkspace:

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.git = GitTools(repo_path)
        self.files = FileTools(repo_path)

    def prepare(self, branch_name):
        current_branch = self.git.current_branch()

        if current_branch != branch_name:
            self.git.switch_branch(branch_name)

        return self.git.current_branch()

    def get_status(self):
        return self.git.status()

    def get_diff(self):
        return self.git.diff()

    def apply_changes(self, changes):
        for change in changes:
            self.files.write(
                change["path"],
                change["content"]
            )