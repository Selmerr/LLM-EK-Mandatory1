from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from .artifacts import ArtifactStore
from .config import WorkflowConfig
from .llm import ChatMessage, OllamaClient
from .prompts import SYSTEM_PROMPT, file_creation_prompt, implementation_prompt, role_prompt
from .repository import CommandResult, Repository, parse_file_blocks


@dataclass
class WorkflowState:
    repo_tree: str
    architecture: str = ""
    backlog: str = ""
    quality_plan: str = ""
    quality_report: str = ""
    launch_report: str = ""
    documentation: str = ""
    deployment_report: str = ""
    implementation_notes: list[str] = field(default_factory=list)
    command_results: list[CommandResult] = field(default_factory=list)


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
            "Create one Markdown file worth of Architecture Decision Records for the project. Include ADR sections only. The ADRs must be specific enough for a tech lead to derive implementation tasks.",
            num_predict=768,
        )

        state.architecture = architecture
        self.artifacts.write("architecture/adrs.md", architecture)

    def _tech_lead(self, state: WorkflowState) -> None:
        implementers = ", ".join(self._implementation_roles())
        backlog = self._ask_role(
            "tech_lead",
            state,
            f"Create an implementation backlog only. Do not create an ADR or architecture document. Use this exact structure for each ticket: ## Ticket T<n>: <title>; Assigned worker: <one of {implementers}>; Scope: <what to build>; Files: <paths under {self.repository.root.name}/> ; Acceptance criteria: <checkable outcomes>; Dependencies: <ticket ids or none>. Assign work across these workers: {implementers}. The tickets must create the target project from scratch if it does not exist. Creating folders under {self.repository.root.name}/ is allowed and should be expressed as file paths in the Files field. The backlog must include launch/setup files required to run and test the project, such as package manifests, entrypoints, scripts, environment examples, and frontend bootstrapping files when relevant.",
            num_predict=768,
        )
        if not _valid_backlog(backlog, self._implementation_roles()):
            state.backlog = backlog
            backlog = self._ask_role(
                "tech_lead",
                state,
                f"The previous tech lead output was not a valid implementation backlog. Rewrite it as tickets only, using the exact fields: Assigned worker, Scope, Files, Acceptance criteria, Dependencies. Assign tickets across: {implementers}. All implementation file paths must be under {self.repository.root.name}/. Include any needed folders by using nested file paths under {self.repository.root.name}/. Include launch/setup files needed to install, run, and test the generated project.",
                num_predict=768,
            )
        state.backlog = backlog
        self.artifacts.write("tickets/backlog.md", backlog)

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
                self.artifacts.write(f"implementation/{worker}.files.txt", output)
                generated_outputs[worker] = output

        print("[workflow] all implementation workers finished; applying generated files sequentially", flush=True)
        for worker in self._implementation_roles():
            output = generated_outputs.get(worker, "")
            blocks = parse_file_blocks(output)
            print(f"\n--- {worker} generated {len(blocks)} file block(s); awaiting apply approval ---\n", flush=True)
            result = self.repository.apply_file_blocks(blocks, f"{worker} file bundle")
            state.command_results.append(result)
            state.implementation_notes.append(f"{worker}: file bundle apply return code {result.returncode}")

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

    def _testing_and_quality(self, state: WorkflowState) -> None:
        state.repo_tree = self.repository.tree()
        quality_plan = self._ask_file_role(
            role_name="tester",
            state=state,
            task="Create actual test files for the project that exists in the target repository, then include commands to run those tests. The tests must be real executable tests, not a testing plan.",
            num_predict=1536,
        )
        state.quality_plan = quality_plan
        self.artifacts.write("quality/tester-output.txt", quality_plan)
        test_apply = self.repository.apply_file_blocks(parse_file_blocks(quality_plan), "tester file bundle")
        state.command_results.append(test_apply)

        results: list[CommandResult] = []
        for command in _commands_from_quality_plan(quality_plan):
            results.append(self.repository.run(command))
        state.command_results.extend(results)

        report = ["# Quality Report", ""]
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
        report.extend(
            [
                "## Known Limitations",
                "",
                "- Local model output quality depends on the selected model and hardware.",
                "- Quality commands are generated by the tester role from prior artifacts and require human approval before execution.",
            ]
        )
        state.quality_report = "\n".join(report)
        self.artifacts.write("quality/quality-report.md", state.quality_report)

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
        deployment_report = self._ask_file_role(
            role_name="deployment_validator",
            state=state,
            task="Create deployment validation files for the generated project. Include a GitHub Actions workflow where appropriate and any config/scripts needed to validate deployability. Include COMMAND lines for safe validation commands.",
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
                "## Commands",
                *(f"- `{result.command}` -> {result.returncode}" for result in state.command_results),
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


def _valid_backlog(backlog: str, implementers: list[str]) -> bool:
    lowered = backlog.lower()
    has_ticket_shape = "assigned worker" in lowered and "acceptance criteria" in lowered
    assigns_worker = any(worker in backlog for worker in implementers)
    looks_like_architecture_doc = lowered.count("adr") > 1 or "## decision" in lowered
    return has_ticket_shape and assigns_worker and not looks_like_architecture_doc


def _commands_from_quality_plan(quality_plan: str) -> list[str]:
    commands: list[str] = []
    for line in quality_plan.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("COMMAND:"):
            command = stripped.split(":", 1)[1].strip()
            if command:
                commands.append(command)
    return commands


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
