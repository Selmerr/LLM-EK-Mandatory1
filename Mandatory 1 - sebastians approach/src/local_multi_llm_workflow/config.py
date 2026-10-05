from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    repository_path: Path
    artifact_path: Path


@dataclass(frozen=True)
class ModelEndpointConfig:
    base_url: str


@dataclass(frozen=True)
class RoleConfig:
    temperature: float


@dataclass(frozen=True)
class ModelProfileConfig:
    endpoint: str
    model: str


@dataclass(frozen=True)
class ControlConfig:
    ask_before_commands: bool
    ask_before_file_edits: bool
    max_backlog_revision_iterations: int
    max_implementation_completion_iterations: int
    max_implementation_verification_iterations: int
    max_repair_iterations: int
    commit_after_each_stage: bool


@dataclass(frozen=True)
class WorkflowConfig:
    goal: str
    project: ProjectConfig
    endpoints: dict[str, ModelEndpointConfig]
    profiles: dict[str, ModelProfileConfig]
    active_profile: str
    roles: dict[str, RoleConfig]
    controls: ControlConfig


def load_config(path: str | Path, profile: str | None = None) -> WorkflowConfig:
    config_path = Path(path).resolve()
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a YAML mapping in {config_path}")

    base_dir = config_path.parent.parent
    project = raw["project"]
    controls = raw["controls"]

    roles = {
        name: RoleConfig(
            temperature=float(value.get("temperature", 0.1)),
        )
        for name, value in raw["roles"].items()
    }
    profiles = {
        name: ModelProfileConfig(
            endpoint=str(value["endpoint"]),
            model=str(value["model"]),
        )
        for name, value in raw["model_profiles"].items()
    }
    active_profile = profile or str(raw.get("default_profile", next(iter(profiles))))
    if active_profile not in profiles:
        known = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown model profile {active_profile!r}. Known profiles: {known}")

    raw_endpoints = raw.get("ollama_endpoints", {"ollama_primary": {"base_url": "http://localhost:11434"}})
    endpoints = {
        name: ModelEndpointConfig(base_url=str(value["base_url"]).rstrip("/"))
        for name, value in raw_endpoints.items()
    }

    return WorkflowConfig(
        goal=str(raw["goal"]),
        project=ProjectConfig(
            repository_path=_resolve_path(base_dir, project["repository_path"]),
            artifact_path=_resolve_path(base_dir, project["artifact_path"]) / active_profile,
        ),
        endpoints=endpoints,
        profiles=profiles,
        active_profile=active_profile,
        roles=roles,
        controls=ControlConfig(
            ask_before_commands=bool(controls.get("ask_before_commands", True)),
            ask_before_file_edits=bool(controls.get("ask_before_file_edits", True)),
            max_backlog_revision_iterations=int(controls.get("max_backlog_revision_iterations", 4)),
            max_implementation_completion_iterations=int(
                controls.get("max_implementation_completion_iterations", 1)
            ),
            max_implementation_verification_iterations=int(
                controls.get("max_implementation_verification_iterations", 1)
            ),
            max_repair_iterations=int(controls.get("max_repair_iterations", 1)),
            commit_after_each_stage=bool(controls.get("commit_after_each_stage", False)),
        ),
    )


def _resolve_path(base_dir: Path, value: Any) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()
