# Local Multi-LLM Workflow

This project is a runnable local coding workflow for the assignment. It calls Ollama's native `/api/chat` endpoint, supports multiple local Ollama endpoints through YAML configuration, separates software-engineering responsibilities into roles, and writes reviewable artifacts to disk.

The workflow is designed for model comparison. `configs/workflow.yaml` defines four model profiles:

- `qwen3_4b`: every role uses `qwen3:4b`
- `qwen2_5_coder_3b`: every role uses `qwen2.5-coder:3b`
- `qwen2_5_coder_7b`: every role uses `qwen2.5-coder:7b`
- `llama3_1_8b`: every role uses `llama3.1:8b`

Run the same workflow once per profile, then compare the generated project files, artifacts, and quality reports.
Each stage is informed by artifacts produced earlier in the chain. The tech lead stage generates the backlog and assigns tickets to implementation workers; implementation is not hardcoded in the runner. The implementers generate actual project files under `demo_repo/`, the tester generates actual test files and commands, the documenter writes documentation files, and the deployment validator writes deployment validation files.

The tech lead output is verified before implementation starts. The verifier requires multiple tickets, at least one ticket per implementation worker, concrete file paths under `demo_repo/`, acceptance criteria, and dependency fields. If the backlog is weak, the workflow asks the tech lead to revise it. If the model still cannot produce a valid backlog after the configured attempts, the runner creates a conservative fallback backlog so implementation starts from usable tickets instead of a vague one-ticket plan.

If the generated tests fail, the workflow starts a bounded repair loop. Failed command output and a compact snapshot of the current project files are sent back to the model, the model generates a repair file bundle under `demo_repo/`, and the workflow reruns the same test commands after a repair is applied. The retry limit is configured with `max_repair_iterations` in `configs/workflow.yaml`.

Test commands are only run after the generated test files have been applied successfully. Commands execute with `demo_repo/` as the working directory, and common generated prefixes such as `cd demo_repo &&` are stripped before execution.

Implementation workers are also checked against their assigned tickets. The workflow reads concrete paths from the tech lead backlog `Files:` fields, compares them with the worker's generated `BEGIN_FILE` blocks, and asks the worker for a completion pass when required files are missing. This validation is ticket-driven, so it works for any project shape rather than assuming a frontend/backend split.

After implementation file bundles are applied, the workflow runs a second verifier against the actual filesystem. It checks that every concrete file path assigned to each worker exists under `demo_repo/` and is non-empty. Missing files trigger a verifier fix pass, and the result is saved in `artifacts/<profile>/implementation/verification-report.md`.

## Quick Demo

```powershell
python -m pip install -e .
python run_workflow.py --profile qwen2_5_coder_3b
```

For full reproduction steps, see `SETUP_GUIDE.md`.

Generated workflow artifacts appear in:

```text
artifacts/<profile-name>/
```

The workflow asks model agents to create the demo project folder and files. The exact file structure is decided by the generated ADR and backlog, but all files must be under:

```text
demo_repo/
```

## Ollama Setup

Start two Ollama endpoints. The first can use Ollama's default port:

```powershell
ollama pull qwen3:4b
ollama pull llama3.1:8b
ollama serve
```

For the second endpoint, run another Ollama server on a different machine or on another local port. One local option is:

```powershell
$env:OLLAMA_HOST="127.0.0.1:11435"
ollama serve
```

`configs/workflow.yaml` maps `qwen3_4b` to `ollama_primary` and `llama3_1_8b` to `ollama_secondary`.

Run the default coder model through all roles:

```powershell
python run_workflow.py
```

Or select it explicitly:

```powershell
python run_workflow.py --profile qwen2_5_coder_3b
```

Run the larger coder model for a stronger but slower comparison:

```powershell
python run_workflow.py --profile qwen2_5_coder_7b
```

The runner keeps Ollama models warm, shows progress while each role generates output, and asks before creating folders/files or running commands.

Run Llama through all roles:

```powershell
python run_workflow.py --profile llama3_1_8b
```

The workflow asks before applying model-generated files or running commands unless those controls are disabled in the workflow config.

For a fair comparison, run each profile from the same repository state. The simplest approach is to remove `demo_repo/` before each run so each model has to create the same project from scratch.

## Assignment Coverage

- Multiple local endpoints: configured under `ollama_endpoints` in `configs/workflow.yaml`.
- Role/model profiles: configured in `configs/workflow.yaml`.
- Architecture artifacts: `artifacts/<profile>/architecture/architecture.md`, including component decomposition, interface contracts, deployment topology/constraints, and ADRs.
- Tech-lead tickets: `artifacts/<profile>/tickets/backlog.md`.
- Tech-lead verification: `artifacts/<profile>/tickets/backlog-verification.md`.
- Multiple implementation workers: `implementer_a` and `implementer_b`.
- Ticket coverage validation: implementation outputs and applied repository files are checked against the concrete file paths listed in assigned backlog tickets.
- Testing and quality: `artifacts/<profile>/quality/tester-output.txt`, `quality-report.md`, and repair iteration artifacts when tests fail.
- Documentation: creates documentation files under `demo_repo/`.
- Deployment validation: creates a deterministic deployment checklist and GitHub Actions workflow, then asks the deployment validator role for project-specific improvements.
- Control: ask-before-run and ask-before-edit review generated file bundles before applying them.
- Reproducibility: artifacts and repository changes are reviewable with git.
