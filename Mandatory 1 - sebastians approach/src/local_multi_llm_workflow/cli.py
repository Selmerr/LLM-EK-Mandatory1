from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .workflow import WorkflowRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local multi-LLM coding workflow.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the configured workflow.")
    run_parser.add_argument("--config", default="configs/workflow.yaml", help="Path to workflow YAML config.")
    run_parser.add_argument("--profile", help="Model profile to run, for example qwen3_4b or llama3_1_8b.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        config_path = Path(args.config)
        config = load_config(config_path, profile=args.profile)
        state = WorkflowRunner(config).run()
        print(f"Workflow completed for profile {config.active_profile!r}.")
        print(f"Artifacts: {config.project.artifact_path}")
        print(f"Repository: {config.project.repository_path}")
        print(f"Commands run: {len(state.command_results)}")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
