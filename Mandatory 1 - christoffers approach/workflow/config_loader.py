from pathlib import Path

import yaml


class WorkflowConfig:

    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        config_path = project_root / "config" / "workflow.yaml"

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def get_model_for_role(self, role):
        model_profile = self.config["roles"][role]["model"]
        return self.config["models"][model_profile]["model"]