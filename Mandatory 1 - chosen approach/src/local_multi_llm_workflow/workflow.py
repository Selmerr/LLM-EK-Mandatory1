from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from .artifacts import ArtifactStore
from .config import WorkflowConfig
from .llm import ChatMessage, OllamaClient
from .prompts import SYSTEM_PROMPT, file_creation_prompt, implementation_prompt, role_prompt
from .repository import CommandResult, FileBlock, Repository, parse_file_blocks


@dataclass
class WorkflowState:
    repo_tree: str
    architecture: str = ""
    backlog: str = ""
    backlog_notes: list[str] = field(default_factory=list)
    quality_plan: str = ""
    quality_report: str = ""
    launch_report: str = ""
    documentation: str = ""
    deployment_report: str = ""
    implementation_notes: list[str] = field(default_factory=list)
    command_results: list[CommandResult] = field(default_factory=list)
    repair_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BacklogVerification:
    valid: bool
    ticket_count: int
    issues: list[str]
    worker_files: dict[str, list[str]]

    def report(self) -> str:
        lines = [
            "# Backlog Verification",
            "",
            f"- Result: {'PASS' if self.valid else 'FAIL'}",
            f"- Ticket count: {self.ticket_count}",
            "",
            "## Worker File Coverage",
        ]
        for worker, files in sorted(self.worker_files.items()):
            lines.append(f"- {worker}: {len(files)} concrete file(s)")
            for path in files:
                lines.append(f"  - {path}")
        lines.extend(["", "## Issues"])
        if self.issues:
            lines.extend(f"- {issue}" for issue in self.issues)
        else:
            lines.append("- None")
        return "\n".join(lines)


class WorkflowRunner:
    def __init__(self, config: WorkflowConfig) -> None:
        self.config = config
        self.artifacts = ArtifactStore(config.project.artifact_path)
        self.repository = Repository(
            config.project.repository_path,
            ask_before_commands=config.controls.ask_before_commands,
            ask_before_file_edits=config.controls.ask_before_file_edits,
        )
        self.client = OllamaClient()

    def run(self) -> WorkflowState:
        state = WorkflowState(repo_tree=self.repository.tree())
        print("[workflow] starting architecture stage", flush=True)
        self._architecture(state)
        print("[workflow] starting tech lead stage", flush=True)
        self._tech_lead(state)
        print("[workflow] starting implementation stage", flush=True)
        self._implementation(state)
        print("[workflow] verifying implementation against assigned tickets", flush=True)
        self._verify_implementation(state)
        print("[workflow] validating launch/setup files", flush=True)
        self._launch_files(state)
        print("[workflow] starting testing/quality stage", flush=True)
        self._testing_and_quality(state)
        print("[workflow] deriving documentation artifacts", flush=True)
        self._documentation(state)
        print("[workflow] deriving deployment validation artifacts", flush=True)
        self._deployment_validation(state)
        print("[workflow] writing final summary", flush=True)
        self._final_report(state)
        return state

    def _architecture(self, state: WorkflowState) -> None:
        architecture = self._ask_role(
            "architect",
            state,
            (
                "Create one Markdown architecture artifact with these exact top-level sections: "
                "# Architecture Artifact; ## Component Decomposition; ## Interface Contracts; "
                "## Deployment Topology and Constraints; ## Architecture Decision Records. "
                "The component section must define responsibilities. The interface section must include "
                "API shapes or equivalent contracts. The topology section must describe runtime/deployment "
                "constraints. The ADR section must contain concrete decisions that a tech lead can convert into tickets."
            ),
            num_predict=1280,
        )

        state.architecture = architecture
        self.artifacts.write("architecture/architecture.md", architecture)

    def _tech_lead(self, state: WorkflowState) -> None:
        backlog = self._tech_lead_output(state)
        max_iterations = max(0, self.config.controls.max_backlog_revision_iterations)
        verification = _verify_backlog(backlog, self._implementation_roles(), self.repository.root.name)

        for iteration in range(1, max_iterations + 1):
            self.artifacts.write(
                f"tickets/backlog-verification-attempt-{iteration}.md",
                verification.report(),
            )
            if verification.valid:
                break

            print(
                f"[workflow] tech lead backlog failed verification; requesting revision {iteration}/{max_iterations}",
                flush=True,
            )
            state.backlog = backlog
            state.backlog_notes.append(
                f"Backlog verification attempt {iteration} failed: {'; '.join(verification.issues)}"
            )
            backlog = self._tech_lead_output(state, verification.report())
            verification = _verify_backlog(backlog, self._implementation_roles(), self.repository.root.name)

        self.artifacts.write("tickets/backlog-verification.md", verification.report())
        if not verification.valid:
            state.backlog_notes.append(
                "Model-generated backlog did not pass verification after refinement attempts; using deterministic fallback backlog."
            )
            backlog = _fallback_backlog(self.config.goal, self._implementation_roles(), self.repository.root.name)
            verification = _verify_backlog(backlog, self._implementation_roles(), self.repository.root.name)
            self.artifacts.write("tickets/backlog-fallback.md", backlog)
            self.artifacts.write("tickets/backlog-verification.md", verification.report())
            if verification.valid:
                state.backlog_notes.append("Fallback backlog verification passed.")
            else:
                state.backlog_notes.append(
                    f"Fallback backlog verification still has issues: {'; '.join(verification.issues)}"
                )

        if verification.valid:
            state.backlog_notes.append("Backlog verification passed.")
        else:
            state.backlog_notes.append("Backlog verification did not pass, but the run will continue with the best available fallback backlog.")
        state.backlog = backlog
        self.artifacts.write("tickets/backlog.md", backlog)

    def _tech_lead_output(self, state: WorkflowState, verification_feedback: str | None = None) -> str:
        implementers = ", ".join(self._implementation_roles())
        feedback = (
            "\n\nPrevious backlog verification feedback:\n"
            f"{verification_feedback}\n\nRewrite the backlog to fix every issue above."
            if verification_feedback
            else ""
        )
        return self._ask_role(
            "tech_lead",
            state,
            (
                "Create an implementation backlog only. Do not create an ADR or architecture document. "
                "Use this exact structure for each ticket: ## Ticket T<n>: <title>; "
                f"Assigned worker: <one of {implementers}>; "
                "Scope: <what to build>; "
                f"Files: <concrete file paths under {self.repository.root.name}/> ; "
                "Acceptance criteria: <checkable outcomes>; Dependencies: <ticket ids or none>. "
                f"Create at least {max(2, len(self._implementation_roles()))} tickets and assign at least one ticket to every implementation worker: {implementers}. "
                "The backlog must cover enough work to create the generated project from scratch, not just describe it. "
                f"Creating folders under {self.repository.root.name}/ is allowed and must be expressed as concrete file paths in the Files field. "
                "Do not use wildcards, folder-only paths, placeholders, or vague entries like etc. in the Files field. "
                "Include launch/setup files required to run and test the project, such as package manifests, entrypoints, scripts, environment examples, and frontend bootstrapping files when relevant."
                f"{feedback}"
            ),
            num_predict=1280,
        )

    def _implementation(self, state: WorkflowState) -> None:
        generated_outputs: dict[str, str] = {}
        with ThreadPoolExecutor(max_workers=max(1, len(self._implementation_roles()))) as executor:
            futures = {
                executor.submit(self._implementation_worker_output, worker, state): worker
                for worker in self._implementation_roles()
            }
            for future in as_completed(futures):
                worker = futures[future]
                output = _strip_fences(future.result())
                output = self._complete_missing_implementation_files(worker, state, output)
                self.artifacts.write(f"implementation/{worker}.files.txt", output)
                generated_outputs[worker] = output

        print("[workflow] all implementation workers finished; applying generated files sequentially", flush=True)
        for worker in self._implementation_roles():
            output = generated_outputs.get(worker, "")
            blocks = parse_file_blocks(output)
            missing = _missing_required_paths(
                required=_required_files_for_worker(state.backlog, worker, self.repository.root.name),
                blocks=blocks,
            )
            if missing:
                formatted = ", ".join(missing)
                state.implementation_notes.append(f"{worker}: missing required ticket files after completion pass: {formatted}")
            print(f"\n--- {worker} generated {len(blocks)} file block(s); awaiting apply approval ---\n", flush=True)
            result = self.repository.apply_file_blocks(blocks, f"{worker} file bundle")
            state.command_results.append(result)
            state.implementation_notes.append(f"{worker}: file bundle apply return code {result.returncode}")

    def _verify_implementation(self, state: WorkflowState) -> None:
        max_iterations = max(0, self.config.controls.max_implementation_verification_iterations)
        verification_lines = ["# Implementation Verification", ""]

        for worker in self._implementation_roles():
            required = _required_files_for_worker(state.backlog, worker, self.repository.root.name)
            if not required:
                note = f"{worker}: no concrete required files found in assigned tickets"
                verification_lines.append(f"- {note}")
                state.implementation_notes.append(note)
                continue

            missing = self.repository.missing_or_empty_paths(required)
            if not missing:
                note = f"{worker}: all {len(required)} required ticket file(s) exist after apply"
                verification_lines.append(f"- {note}")
                state.implementation_notes.append(note)
                continue

            verification_lines.append(
                f"- {worker}: missing or empty after apply: {', '.join(missing)}"
            )
            for iteration in range(1, max_iterations + 1):
                print(
                    f"[workflow] {worker} verification found {len(missing)} missing/empty file(s); requesting fix {iteration}/{max_iterations}",
                    flush=True,
                )
                state.repo_tree = self.repository.tree()
                verifier_output = self._implementation_verification_fix_output(
                    worker=worker,
                    state=state,
                    missing_paths=missing,
                    iteration=iteration,
                )
                self.artifacts.write(
                    f"implementation/{worker}.verification-fix-{iteration}.files.txt",
                    verifier_output,
                )
                result = self.repository.apply_file_blocks(
                    parse_file_blocks(verifier_output),
                    f"{worker} verification fix {iteration} bundle",
                )
                state.command_results.append(result)
                state.implementation_notes.append(
                    f"{worker}: verification fix {iteration} apply return code {result.returncode}"
                )
                if not result.passed:
                    verification_lines.append(
                        f"- {worker}: verification fix {iteration} was not applied; remaining: {', '.join(missing)}"
                    )
                    continue

                missing = self.repository.missing_or_empty_paths(required)
                if not missing:
                    verification_lines.append(
                        f"- {worker}: all required ticket files exist after verification fix {iteration}"
                    )
                    state.implementation_notes.append(
                        f"{worker}: all required ticket files exist after verification fix {iteration}"
                    )
                    break

            if missing:
                verification_lines.append(
                    f"- {worker}: still missing or empty after verification: {', '.join(missing)}"
                )
                state.implementation_notes.append(
                    f"{worker}: still missing or empty after verification: {', '.join(missing)}"
                )

        state.repo_tree = self.repository.tree()
        self.artifacts.write("implementation/verification-report.md", "\n".join(verification_lines))

    def _complete_missing_implementation_files(self, worker: str, state: WorkflowState, output: str) -> str:
        required = _required_files_for_worker(state.backlog, worker, self.repository.root.name)
        if not required:
            state.implementation_notes.append(f"{worker}: no concrete required file paths found in assigned tickets")
            return output

        combined_output = output
        max_iterations = max(0, self.config.controls.max_implementation_completion_iterations)
        for iteration in range(1, max_iterations + 1):
            blocks = parse_file_blocks(combined_output)
            missing = _missing_required_paths(required=required, blocks=blocks)
            if not missing:
                state.implementation_notes.append(f"{worker}: generated all concrete files required by assigned tickets")
                return combined_output

            print(
                f"[workflow] {worker} missed {len(missing)} required ticket file(s); requesting completion pass {iteration}/{max_iterations}",
                flush=True,
            )
            completion = self._implementation_completion_output(worker, state, combined_output, missing)
            self.artifacts.write(f"implementation/{worker}.completion-{iteration}.files.txt", completion)
            combined_output = combined_output.rstrip() + "\n\n" + _strip_fences(completion)

        missing = _missing_required_paths(required=required, blocks=parse_file_blocks(combined_output))
        if missing:
            state.implementation_notes.append(
                f"{worker}: completion pass still missing {len(missing)} required file(s): {', '.join(missing)}"
            )
        else:
            state.implementation_notes.append(f"{worker}: generated all concrete files required by assigned tickets")
        return combined_output

    def _launch_files(self, state: WorkflowState) -> None:
        state.repo_tree = self.repository.tree()
        launch_output = self._ask_file_role(
            role_name=self._implementation_roles()[0],
            state=state,
            task=(
                "Inspect the current generated project and create only missing launch/setup files needed to install, run, "
                "and test it. Examples: package.json, client/package.json, server/package.json, vite/index.html/main.jsx, "
                ".env.example, scripts, or other runtime entry/config files. Do not rewrite existing source files unless a "
                "small fix is required for launch commands to work. Include COMMAND lines for safe local validation commands."
            ),
            num_predict=1536,
        )
        state.launch_report = launch_output
        self.artifacts.write("implementation/launch-files-output.txt", launch_output)
        result = self.repository.apply_file_blocks(parse_file_blocks(launch_output), "launch files bundle")
        state.command_results.append(result)
        state.implementation_notes.append(f"launch files: file bundle apply return code {result.returncode}")

    def _implementation_worker_output(self, worker: str, state: WorkflowState) -> str:
            role = self.config.roles[worker]
            profile = self.config.profiles[self.config.active_profile]
            assignment = _assignment_for_worker(state.backlog, worker)
            prompt = implementation_prompt(
                worker=worker,
                goal=self.config.goal,
                repo_tree=state.repo_tree,
                context=f"Architecture summary:\n{_clip(state.architecture, 2500)}\n\nBacklog summary:\n{_clip(state.backlog, 1200)}",
                task=assignment,
                target_root=self.repository.root.name,
            )
            return self.client.complete(
                base_url=self._endpoint_url(profile.endpoint),
                model=profile.model,
                temperature=role.temperature,
                messages=[
                    ChatMessage("system", SYSTEM_PROMPT),
                    ChatMessage("user", prompt),
                ],
                num_predict=1536,
                progress_label=f"{worker}:{profile.model}",
            )

    def _implementation_completion_output(
        self,
        worker: str,
        state: WorkflowState,
        previous_output: str,
        missing_paths: list[str],
    ) -> str:
        role = self.config.roles[worker]
        profile = self.config.profiles[self.config.active_profile]
        assignment = _assignment_for_worker(state.backlog, worker)
        prompt = implementation_prompt(
            worker=worker,
            goal=self.config.goal,
            repo_tree=state.repo_tree,
            context=(
                "The previous implementation output did not include every concrete file listed in the assigned ticket Files fields. "
                "Generate only the missing required files. Do not repeat files already generated.\n\n"
                f"Missing required files:\n{chr(10).join(f'- {path}' for path in missing_paths)}\n\n"
                f"Previously generated file paths:\n{chr(10).join(f'- {path}' for path in _block_paths(parse_file_blocks(previous_output)))}"
            ),
            task=assignment,
            target_root=self.repository.root.name,
        )
        return self.client.complete(
            base_url=self._endpoint_url(profile.endpoint),
            model=profile.model,
            temperature=role.temperature,
            messages=[
                ChatMessage("system", SYSTEM_PROMPT),
                ChatMessage("user", prompt),
            ],
            num_predict=1536,
            progress_label=f"{worker}-completion:{profile.model}",
        )

    def _implementation_verification_fix_output(
        self,
        worker: str,
        state: WorkflowState,
        missing_paths: list[str],
        iteration: int,
    ) -> str:
        role = self.config.roles[worker]
        profile = self.config.profiles[self.config.active_profile]
        assignment = _assignment_for_worker(state.backlog, worker)
        prompt = implementation_prompt(
            worker=worker,
            goal=self.config.goal,
            repo_tree=state.repo_tree,
            context=(
                f"Post-apply verification iteration {iteration} found that required files are missing or empty in the actual repository. "
                "Generate full file contents for exactly these missing or empty files. Do not return a plan. Do not repeat existing files unless they are listed below.\n\n"
                f"Missing or empty files:\n{chr(10).join(f'- {path}' for path in missing_paths)}\n\n"
                f"Current repository snapshot:\n{self.repository.snapshot(max_files=24, max_chars=18000)}"
            ),
            task=assignment,
            target_root=self.repository.root.name,
        )
        return self.client.complete(
            base_url=self._endpoint_url(profile.endpoint),
            model=profile.model,
            temperature=role.temperature,
            messages=[
                ChatMessage("system", SYSTEM_PROMPT),
                ChatMessage("user", prompt),
            ],
            num_predict=1536,
            progress_label=f"{worker}-verify:{profile.model}",
        )

    def _testing_and_quality(self, state: WorkflowState) -> None:
        state.repo_tree = self.repository.tree()
        quality_plan = self._tester_output(state)
        quality_blocks = parse_file_blocks(quality_plan)
        if not quality_blocks:
            print("[workflow] tester returned no file blocks; requesting strict test-file retry", flush=True)
            quality_plan = self._tester_output(state, strict_retry=True)
            quality_blocks = parse_file_blocks(quality_plan)

        state.quality_plan = quality_plan
        self.artifacts.write("quality/tester-output.txt", quality_plan)
        test_apply = self.repository.apply_file_blocks(quality_blocks, "tester file bundle")
        state.command_results.append(test_apply)

        commands = _commands_from_quality_plan(quality_plan)
        if not test_apply.passed:
            state.repair_notes.append(
                "Testing commands were not run because the tester file bundle was not applied."
            )
            state.quality_report = _quality_report([], state.repair_notes)
            self.artifacts.write("quality/quality-report.md", state.quality_report)
            return
        if not commands:
            state.repair_notes.append("Testing commands were not run because the tester did not provide COMMAND lines.")
            state.quality_report = _quality_report([], state.repair_notes)
            self.artifacts.write("quality/quality-report.md", state.quality_report)
            return

        results = self._run_quality_commands(commands)
        state.command_results.extend(results)

        state.quality_report = _quality_report(results, state.repair_notes)
        self.artifacts.write("quality/quality-report.md", state.quality_report)
        self._repair_failed_quality(state, commands, results)
        self.artifacts.write("quality/quality-report.md", state.quality_report)

    def _tester_output(self, state: WorkflowState, strict_retry: bool = False) -> str:
        strict_instruction = (
            "Your previous tester response did not contain any BEGIN_FILE test files, so no tests could be created. "
            "This time you must return at least one complete BEGIN_FILE block for an executable test file. "
            if strict_retry
            else ""
        )
        return self._ask_file_role(
            role_name="tester",
            state=state,
            task=(
                f"{strict_instruction}"
                "Create actual executable test files for the project that exists in the target repository, then include commands to run those tests. "
                "The tests must be real executable tests, not a testing plan. "
                f"COMMAND lines are run with the working directory already set to {self.repository.root.name}/, so do not prefix commands with cd {self.repository.root.name}. "
                "Use commands that can run from the target repository root."
            ),
            num_predict=1536,
        )

    def _run_quality_commands(self, commands: list[str]) -> list[CommandResult]:
        return [self.repository.run(command) for command in commands]

    def _repair_failed_quality(
        self,
        state: WorkflowState,
        commands: list[str],
        results: list[CommandResult],
    ) -> None:
        max_iterations = max(0, self.config.controls.max_repair_iterations)
        if not commands or max_iterations == 0:
            return

        current_results = results
        for iteration in range(1, max_iterations + 1):
            failed_results = _repairable_failures(current_results)
            if not failed_results:
                return

            print(f"[workflow] tests failed; starting repair iteration {iteration}/{max_iterations}", flush=True)
            state.repo_tree = self.repository.tree()
            repair_output = self._quality_repair_output(state, failed_results, iteration)
            self.artifacts.write(f"quality/repair-iteration-{iteration}.files.txt", repair_output)
            repair_blocks = parse_file_blocks(repair_output)
            if not repair_blocks:
                print(
                    f"[workflow] repair iteration {iteration} returned no file blocks; requesting strict file-only retry",
                    flush=True,
                )
                repair_output = self._quality_repair_output(
                    state,
                    failed_results,
                    iteration,
                    strict_retry=True,
                )
                self.artifacts.write(f"quality/repair-iteration-{iteration}-retry.files.txt", repair_output)
                repair_blocks = parse_file_blocks(repair_output)

            repair_apply = self.repository.apply_file_blocks(
                repair_blocks,
                f"quality repair iteration {iteration} bundle",
            )
            state.command_results.append(repair_apply)
            state.repair_notes.append(
                f"Repair iteration {iteration}: file bundle apply return code {repair_apply.returncode}"
            )
            if not repair_apply.passed:
                state.repair_notes.append(
                    f"Repair iteration {iteration}: tests were not rerun because no repair files were applied"
                )
                continue

            current_results = self._run_quality_commands(commands)
            state.command_results.extend(current_results)
            state.quality_report = _quality_report(current_results, state.repair_notes)
            self.artifacts.write(f"quality/quality-report-after-repair-{iteration}.md", state.quality_report)

    def _quality_repair_output(
        self,
        state: WorkflowState,
        failed_results: list[CommandResult],
        iteration: int,
        strict_retry: bool = False,
    ) -> str:
        strict_instruction = (
            "Your previous repair response did not contain any BEGIN_FILE blocks, so nothing was changed. "
            "This time you must return at least one complete BEGIN_FILE block that edits a source, configuration, or test file. "
            if strict_retry
            else ""
        )
        return self._ask_file_role(
            role_name=self._implementation_roles()[0],
            state=state,
            task=(
                f"Repair iteration {iteration}. The test/quality stage failed. "
                f"{strict_instruction}"
                "Use the failed command output and the current repository snapshot below to make code and tests match each other. "
                "You may edit source files, test files, package/configuration files, or launch files under the target repository. "
                "If the implementation is wrong, fix the implementation. If the generated test is wrong, fix the test. "
                "Do not create a plan or explanation. Return only full replacement file blocks for the files you change.\n\n"
                f"Failed command details:\n{_format_command_results(failed_results)}\n\n"
                f"Current repository file contents:\n{self.repository.snapshot()}"
            ),
            num_predict=2048,
        )

    def _documentation(self, state: WorkflowState) -> None:
        state.repo_tree = self.repository.tree()
        runbook = self._ask_file_role(
            role_name="documenter",
            state=state,
            task="Create documentation files for the generated project, including README.md. Documentation must describe setup, running, testing, and usage of the actual project files.",
            num_predict=1024,
        )
        state.documentation = runbook
        self.artifacts.write("documentation/documenter-output.txt", runbook)
        result = self.repository.apply_file_blocks(parse_file_blocks(runbook), "documenter file bundle")
        state.command_results.append(result)

    def _deployment_validation(self, state: WorkflowState) -> None:
        state.repo_tree = self.repository.tree()
        baseline = self.repository.apply_file_blocks(
            _deployment_baseline_blocks(self.repository.root.name),
            "baseline deployment validation bundle",
        )
        state.command_results.append(baseline)
        state.deployment_report = "Baseline deployment validation files requested."
        self.artifacts.write("deployment/baseline-deployment-output.txt", _deployment_baseline_report())
        state.repo_tree = self.repository.tree()
        deployment_report = self._ask_file_role(
            role_name="deployment_validator",
            state=state,
            task=(
                "Inspect the generated project and improve deployment validation if needed. "
                "A baseline deployment checklist and GitHub Actions workflow may already exist. "
                "Create only additional deployment files or small fixes that make validation more accurate for this project. "
                "Include COMMAND lines for safe local validation commands."
            ),
            num_predict=1536,
        )
        state.deployment_report = deployment_report
        self.artifacts.write("deployment/deployment-output.txt", deployment_report)
        result = self.repository.apply_file_blocks(parse_file_blocks(deployment_report), "deployment file bundle")
        state.command_results.append(result)
        for command in _commands_from_quality_plan(deployment_report):
            state.command_results.append(self.repository.run(command))

    def _final_report(self, state: WorkflowState) -> None:
        final_report = "\n".join(
            [
                "# Workflow Run Summary",
                "",
                f"Goal: {self.config.goal}",
                "",
                "## Roles",
                *[
                    f"- {name}: {self.config.profiles[self.config.active_profile].model} on {self.config.profiles[self.config.active_profile].endpoint}"
                    for name, role in self.config.roles.items()
                ],
                "",
                "## Implementation Notes",
                *(f"- {note}" for note in state.implementation_notes),
                "",
                "## Backlog Verification",
                *(f"- {note}" for note in state.backlog_notes),
                "",
                "## Commands",
                *(f"- `{result.command}` -> {result.returncode}" for result in state.command_results),
                "",
                "## Repair Loop",
                *(f"- {note}" for note in state.repair_notes),
            ]
        )
        self.artifacts.write("run-summary.md", final_report)

    def _ask_role(
        self,
        role_name: str,
        state: WorkflowState,
        task: str,
        num_predict: int = 512,
    ) -> str:
        role = self.config.roles[role_name]
        profile = self.config.profiles[self.config.active_profile]
        prompt = role_prompt(
            role=role_name,
            goal=self.config.goal,
            repo_tree=state.repo_tree,
            context=_role_context(task, state),
        )
        return self.client.complete(
            base_url=self._endpoint_url(profile.endpoint),
            model=profile.model,
            temperature=role.temperature,
            messages=[
                ChatMessage("system", SYSTEM_PROMPT),
                ChatMessage("user", prompt),
            ],
            num_predict=num_predict,
            progress_label=f"{role_name}:{profile.model}",
        )

    def _ask_file_role(
        self,
        role_name: str,
        state: WorkflowState,
        task: str,
        num_predict: int = 1024,
    ) -> str:
        role = self.config.roles[role_name]
        profile = self.config.profiles[self.config.active_profile]
        prompt = file_creation_prompt(
            role=role_name,
            goal=self.config.goal,
            repo_tree=state.repo_tree,
            context=_role_context(task, state),
            target_root=self.repository.root.name,
            task=task,
        )
        return self.client.complete(
            base_url=self._endpoint_url(profile.endpoint),
            model=profile.model,
            temperature=role.temperature,
            messages=[
                ChatMessage("system", SYSTEM_PROMPT),
                ChatMessage("user", prompt),
            ],
            num_predict=num_predict,
            progress_label=f"{role_name}:{profile.model}",
        )

    def _endpoint_url(self, endpoint_name: str) -> str:
        try:
            return self.config.endpoints[endpoint_name].base_url
        except KeyError as exc:
            known = ", ".join(sorted(self.config.endpoints))
            raise ValueError(f"Unknown Ollama endpoint {endpoint_name!r}. Known endpoints: {known}") from exc

    def _implementation_roles(self) -> list[str]:
        return sorted(name for name in self.config.roles if name.startswith("implementer_"))


def _strip_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip() + "\n"
    return stripped + "\n"


def _clip(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n\n[truncated]"


def _assignment_for_worker(backlog: str, worker: str) -> str:
    lines = backlog.splitlines()
    matching: list[str] = []
    capture = False
    for line in lines:
        starts_new_section = line.startswith("#") or line.lower().startswith(("ticket", "- ticket"))
        if starts_new_section and capture and worker not in line:
            capture = False
        if worker in line:
            capture = True
        if capture:
            matching.append(line)

    if matching:
        return "\n".join(matching).strip()

    return (
        f"Use the generated backlog below. Implement only tickets assigned to {worker}. "
        "If assignments are unclear, choose the smallest coherent subset that avoids overlapping with the other worker.\n\n"
        f"{backlog}"
    )


def _required_files_for_worker(backlog: str, worker: str, root_name: str) -> list[str]:
    assignment = _assignment_for_worker(backlog, worker)
    required: list[str] = []
    for line in assignment.splitlines():
        if "files:" not in line.lower():
            continue
        _, files_text = line.split(":", 1)
        required.extend(_extract_concrete_paths(files_text, root_name))
    return sorted(set(required))


def _extract_concrete_paths(text: str, root_name: str) -> list[str]:
    candidates = re.findall(rf"{re.escape(root_name)}[\\/][^\s,;)\]]+", text)
    paths: list[str] = []
    for candidate in candidates:
        normalized = _normalize_generated_path(candidate)
        if _is_concrete_required_file(normalized, root_name):
            paths.append(normalized)
    return paths


def _normalize_generated_path(path: str) -> str:
    return path.strip().strip("`'\".").replace("\\", "/")


def _is_concrete_required_file(path: str, root_name: str) -> bool:
    if not path.startswith(f"{root_name}/"):
        return False
    if path.endswith("/"):
        return False
    if any(marker in path for marker in ["*", "<", ">", "..."]):
        return False
    filename = path.rsplit("/", 1)[-1]
    return "." in filename


def _block_paths(blocks: list[FileBlock]) -> list[str]:
    return sorted({_normalize_generated_path(block.path) for block in blocks})


def _missing_required_paths(required: list[str], blocks: list[FileBlock]) -> list[str]:
    generated = set(_block_paths(blocks))
    return [path for path in required if path not in generated]


def _verify_backlog(backlog: str, implementers: list[str], root_name: str) -> BacklogVerification:
    issues: list[str] = []
    sections = _ticket_sections(backlog)
    minimum_tickets = max(2, len(implementers))

    if len(sections) < minimum_tickets:
        issues.append(
            f"Backlog must contain at least {minimum_tickets} tickets, but found {len(sections)}."
        )

    lowered = backlog.lower()
    if lowered.count("adr") > 1 or "## decision" in lowered:
        issues.append("Backlog looks like an architecture/ADR document instead of implementation tickets.")

    worker_files = {
        worker: _required_files_for_worker(backlog, worker, root_name)
        for worker in implementers
    }
    for worker, files in worker_files.items():
        if worker not in backlog:
            issues.append(f"No ticket is assigned to {worker}.")
        if not files:
            issues.append(f"No concrete implementation files are assigned to {worker}.")

    for index, section in enumerate(sections, start=1):
        section_lower = section.lower()
        if "assigned worker" not in section_lower:
            issues.append(f"Ticket {index} is missing an Assigned worker field.")
        elif not any(worker in section for worker in implementers):
            issues.append(f"Ticket {index} does not assign a known implementation worker.")
        if "scope" not in section_lower:
            issues.append(f"Ticket {index} is missing a Scope field.")
        if "files:" not in section_lower:
            issues.append(f"Ticket {index} is missing a Files field.")
        elif not _extract_concrete_paths(section, root_name):
            issues.append(f"Ticket {index} does not list concrete files under {root_name}/.")
        if "acceptance criteria" not in section_lower:
            issues.append(f"Ticket {index} is missing Acceptance criteria.")
        if "dependencies" not in section_lower:
            issues.append(f"Ticket {index} is missing Dependencies.")

    return BacklogVerification(
        valid=not issues,
        ticket_count=len(sections),
        issues=issues,
        worker_files=worker_files,
    )


def _fallback_backlog(goal: str, implementers: list[str], root_name: str) -> str:
    first_worker = implementers[0] if implementers else "implementer_a"
    second_worker = implementers[1] if len(implementers) > 1 else first_worker
    extra_worker_tickets = []
    for index, worker in enumerate(implementers[2:], start=3):
        extra_worker_tickets.append(
            f"""## Ticket T{index}: Supporting Project Assets
Assigned worker: {worker}
Scope: Add supporting project assets that improve operability and reviewability for the generated application.
Files: {root_name}/docs/runbook.md, {root_name}/scripts/validate.js
Acceptance criteria: The runbook explains local operation and the validation script can be called by package scripts.
Dependencies: T1, T2"""
        )

    tickets = [
        f"""## Ticket T1: Backend REST API
Assigned worker: {first_worker}
Scope: Build the backend REST API and in-memory data layer needed for this goal: {goal}
Files: {root_name}/package.json, {root_name}/server.js, {root_name}/src/dataStore.js, {root_name}/src/routes.js
Acceptance criteria: The API exposes CRUD-style endpoints, returns JSON responses, validates required input, and can be started from an npm script.
Dependencies: none""",
        f"""## Ticket T2: Frontend Client
Assigned worker: {second_worker}
Scope: Build a browser client that uses the REST API for this goal: {goal}
Files: {root_name}/public/index.html, {root_name}/public/styles.css, {root_name}/public/app.js, {root_name}/README.md
Acceptance criteria: The UI can list, create, update, and delete records through the REST API and README describes setup, run, and test commands.
Dependencies: T1""",
        *extra_worker_tickets,
    ]
    return "\n\n".join(tickets)


def _ticket_sections(backlog: str) -> list[str]:
    sections: list[list[str]] = []
    current: list[str] = []
    for line in backlog.splitlines():
        stripped = line.strip()
        starts_ticket = bool(re.match(r"^(#{1,3}\s*)?(-\s*)?ticket\s+t?\d+", stripped, re.IGNORECASE))
        if starts_ticket:
            if current:
                sections.append(current)
            current = [line]
            continue
        if current:
            current.append(line)
    if current:
        sections.append(current)
    return ["\n".join(section).strip() for section in sections if "\n".join(section).strip()]


def _commands_from_quality_plan(quality_plan: str) -> list[str]:
    commands: list[str] = []
    for line in quality_plan.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("COMMAND:"):
            command = stripped.split(":", 1)[1].strip()
            if command:
                commands.append(command)
    return commands


def _repairable_failures(results: list[CommandResult]) -> list[CommandResult]:
    return [
        result
        for result in results
        if not result.passed and result.returncode != 130
    ]


def _quality_report(results: list[CommandResult], repair_notes: list[str]) -> str:
    report = ["# Quality Report", ""]
    if not results:
        report.extend(
            [
                "## Test Results",
                "",
                "No test commands were generated by the tester role.",
                "",
            ]
        )
    for result in results:
        report.extend(
            [
                f"## `{result.command}`",
                "",
                f"- Result: {'PASS' if result.passed else 'FAIL'}",
                f"- Exit code: {result.returncode}",
                "",
                "### stdout",
                "```text",
                result.stdout.strip() or "(empty)",
                "```",
                "",
                "### stderr",
                "```text",
                result.stderr.strip() or "(empty)",
                "```",
                "",
            ]
        )
    if repair_notes:
        report.extend(
            [
                "## Repair Loop",
                "",
                *(f"- {note}" for note in repair_notes),
                "",
            ]
        )
    report.extend(
        [
            "## Known Limitations",
            "",
            "- Local model output quality depends on the selected model and hardware.",
            "- Quality commands are generated by the tester role from prior artifacts and require human approval before execution.",
            "- The repair loop is bounded, so remaining failures may still require manual review after the configured retry limit.",
        ]
    )
    return "\n".join(report)


def _format_command_results(results: list[CommandResult]) -> str:
    chunks: list[str] = []
    for result in results:
        chunks.append(
            "\n".join(
                [
                    f"COMMAND: {result.command}",
                    f"EXIT_CODE: {result.returncode}",
                    "STDOUT:",
                    _clip(result.stdout.strip() or "(empty)", 2500),
                    "STDERR:",
                    _clip(result.stderr.strip() or "(empty)", 2500),
                ]
            )
        )
    return "\n\n".join(chunks)


def _deployment_baseline_blocks(root_name: str) -> list[FileBlock]:
    return [
        FileBlock(
            f"{root_name}/DEPLOYMENT_CHECKLIST.md",
            """# Deployment Validation Checklist

## Required Checks

- [ ] Application dependencies can be installed from committed manifest files.
- [ ] Automated tests pass locally or in CI.
- [ ] Runtime configuration is documented with safe example values.
- [ ] The application has a clear start command.
- [ ] Generated source, tests, documentation, and deployment files are committed together.

## Local Validation

Run the generated project's documented setup and test commands before deployment. If the project contains a Node.js `package.json`, run `npm install` and `npm test` from the folder that contains it. If the project contains a Python `pyproject.toml`, install the project dependencies and run the documented test command.

## Notes

This checklist is created by the workflow so every run has a deployability artifact even when the model-generated deployment validator produces incomplete output.
""",
        ),
        FileBlock(
            f"{root_name}/.github/workflows/validate.yml",
            """name: Validate generated project

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Validate generated project structure
        shell: bash
        run: |
          test -f README.md || test -f package.json || test -f pyproject.toml

      - name: Install and test Node project
        if: ${{ hashFiles('package.json') != '' }}
        shell: bash
        run: |
          npm install
          npm test --if-present

      - name: Install and test Python project
        if: ${{ hashFiles('pyproject.toml') != '' }}
        shell: bash
        run: |
          python -m pip install --upgrade pip
          python -m pip install .
          python -m pytest || python -m unittest discover
""",
        ),
    ]


def _deployment_baseline_report() -> str:
    return """# Baseline Deployment Validation

The workflow creates a deterministic deployment baseline before asking the deployment validator model for project-specific improvements.

Generated baseline files:

- `demo_repo/DEPLOYMENT_CHECKLIST.md`
- `demo_repo/.github/workflows/validate.yml`

This ensures every run contains at least one deployment checklist and one CI validation workflow, satisfying the deployment validation responsibility even if the model output is incomplete.
"""


def _role_context(task: str, state: WorkflowState) -> str:
    command_summary = "\n".join(
        f"- `{result.command}` -> {result.returncode}" for result in state.command_results
    )
    return "\n\n".join(
        part
        for part in [
            task,
            f"Architecture:\n{state.architecture}" if state.architecture else "",
            f"Backlog:\n{state.backlog}" if state.backlog else "",
            f"Implementation notes:\n{chr(10).join(state.implementation_notes)}" if state.implementation_notes else "",
            f"Launch/setup output:\n{state.launch_report}" if state.launch_report else "",
            f"Quality plan:\n{state.quality_plan}" if state.quality_plan else "",
            f"Quality report:\n{state.quality_report}" if state.quality_report else "",
            f"Documentation:\n{state.documentation}" if state.documentation else "",
            f"Command summary:\n{command_summary}" if command_summary else "",
            f"Current repository tree:\n{state.repo_tree}" if state.repo_tree else "",
        ]
        if part
    )


def _derived_documentation(state: WorkflowState) -> str:
    return "\n".join(
        [
            "# Developer Runbook",
            "",
            "## Goal",
            state.backlog.splitlines()[0] if state.backlog else "Generated project from workflow backlog.",
            "",
            "## Repository",
            state.repo_tree,
            "",
            "## Implementation Notes",
            *(f"- {note}" for note in state.implementation_notes),
            "",
            "## Quality",
            state.quality_report or "No quality commands were executed.",
        ]
    )


def _derived_deployment_report(state: WorkflowState) -> str:
    command_summary = "\n".join(
        f"- [{'x' if result.passed else ' '}] `{result.command}` returned {result.returncode}"
        for result in state.command_results
    )
    return "\n".join(
        [
            "# Deployment Validation",
            "",
            "## Checklist",
            "- [x] Workflow artifacts were generated.",
            "- [x] Model-generated file changes were gated by user approval.",
            "- [x] Changed paths were constrained to the target repository.",
            "- [ ] Review quality command results before deployment.",
            "",
            "## Validation Evidence",
            command_summary or "- No commands were executed.",
            "",
            "## Risks",
            "- Local model output may require manual review before production use.",
        ]
    )
