# Local Multi-LLM Workflow

This project is a runnable local coding workflow for the assignment. It calls Ollama's native `/api/chat` endpoint, supports multiple local Ollama endpoints through YAML configuration, separates software-engineering responsibilities into roles, and writes reviewable artifacts to disk.

The workflow is designed for model comparison. `configs/workflow.yaml` defines two model profiles:

- `qwen3_4b`: every role uses `qwen3:4b`
- `qwen2_5_coder_3b`: every role uses `qwen2.5-coder:3b`
- `llama3_1_8b`: every role uses `llama3.1:8b`

Run the same workflow once per profile, then compare the generated project files, artifacts, and quality reports.
Each stage is informed by artifacts produced earlier in the chain. The tech lead stage generates the backlog and assigns tickets to implementation workers; implementation is not hardcoded in the runner. The implementers generate actual project files under `demo_repo/`, the tester generates actual test files and commands, the documenter writes documentation files, and the deployment validator writes deployment validation files.

## Quick Demo

```powershell
python run_workflow.py --profile qwen3_4b
python -m unittest discover tests
```

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
- Architecture artifacts: `artifacts/<profile>/architecture/`.
- Tech-lead tickets: `artifacts/<profile>/tickets/backlog.md`.
- Multiple implementation workers: `implementer_a` and `implementer_b`.
- Testing and quality: `artifacts/<profile>/quality/quality-plan.md` and `artifacts/<profile>/quality/quality-report.md`.
- Documentation: creates documentation files under `demo_repo/`.
- Deployment validation: creates deployment files such as GitHub Actions workflows under `demo_repo/`.
- Control: ask-before-run, ask-before-edit, and diff-before-apply settings.
- Reproducibility: artifacts and repository changes are reviewable with git.
