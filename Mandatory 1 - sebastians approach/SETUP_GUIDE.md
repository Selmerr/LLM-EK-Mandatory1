# Setup Guide

This guide explains how to reproduce the local multi-LLM workflow demo required by the assignment.

## 1. Prerequisites

Install:

- Python 3.10 or newer
- Git
- Ollama
- At least one local coding model, recommended: `qwen2.5-coder:3b`

Optional comparison models:

- `qwen2.5-coder:7b`
- `qwen3:4b`
- `llama3.1:8b`

## 2. Install Models

Pull the default coding model:

```powershell
ollama pull qwen2.5-coder:3b
```

For comparison runs, pull the other configured models:

```powershell
ollama pull qwen2.5-coder:7b
ollama pull qwen3:4b
ollama pull llama3.1:8b
```

## 3. Start Local Endpoints

Start the primary Ollama endpoint:

```powershell
ollama serve
```

The default endpoint is:

```text
http://localhost:11434
```

To use the secondary endpoint on the same machine, open another PowerShell window and run:

```powershell
$env:OLLAMA_HOST="127.0.0.1:11435"
ollama serve
```

The secondary endpoint is:

```text
http://localhost:11435
```

The workflow reads these endpoints from `configs/workflow.yaml`.

## 4. Install Python Dependencies

From the project root, install the Python package in editable mode:

```powershell
python -m pip install -e .
```

## 5. Run the Demo Workflow

Run the default profile:

```powershell
python run_workflow.py
```

Or select the default profile explicitly:

```powershell
python run_workflow.py --profile qwen2_5_coder_3b
```

Run a comparison profile:

```powershell
python run_workflow.py --profile qwen2_5_coder_7b
python run_workflow.py --profile llama3_1_8b
```

During the run, the workflow will ask before writing generated files or running generated commands.

If a generated test command fails, the workflow can ask the model to repair the generated project and rerun the same test command. The repair prompt includes the failed command output and a compact snapshot of the current project files, so the model can edit code and tests to match each other. The number of repair attempts is controlled by:

```yaml
controls:
  max_backlog_revision_iterations: 4
  max_implementation_completion_iterations: 1
  max_implementation_verification_iterations: 1
  max_repair_iterations: 2
```

`max_backlog_revision_iterations` controls how many times the tech lead can be asked to rewrite a weak backlog before the workflow falls back to a deterministic verified backlog.
`max_implementation_completion_iterations` controls how many times a worker can be asked to add files it missed from its assigned ticket `Files:` list.
`max_implementation_verification_iterations` controls how many times a worker can be asked to fix files that are still missing or empty after the generated bundle is applied to `demo_repo/`.

The runner only executes test commands after the tester's file bundle has been applied. Commands run from inside `demo_repo/`, so tester-generated commands should be written as root-relative project commands such as `npm test` rather than `cd demo_repo && npm test`.

## 6. Expected Outputs

The generated application is created under:

```text
demo_repo/
```

The workflow artifacts are written under:

```text
artifacts/<profile>/
```

Important artifacts include:

- `architecture/architecture.md`
- `tickets/backlog.md`
- `tickets/backlog-fallback.md` when the model-generated backlog could not be refined enough
- `tickets/backlog-verification.md`
- `implementation/*.files.txt`
- `implementation/verification-report.md`
- `quality/tester-output.txt`
- `quality/quality-report.md`
- `quality/repair-iteration-<n>.files.txt` when repair attempts are needed
- `documentation/documenter-output.txt`
- `deployment/baseline-deployment-output.txt`
- `deployment/deployment-output.txt`
- `run-summary.md`

The generated project should include actual source files, test files, documentation, and deployment validation files such as:

```text
demo_repo/README.md
demo_repo/DEPLOYMENT_CHECKLIST.md
demo_repo/.github/workflows/validate.yml
```

## 7. Clean Rerun

For a fair model comparison, start each run from the same state. A simple approach is to delete the generated project and artifacts for the profile before rerunning.

In PowerShell:

```powershell
Remove-Item -Recurse -Force demo_repo
Remove-Item -Recurse -Force artifacts\qwen2_5_coder_3b
```

Then run the workflow again.

## 8. What the Demo Proves

A complete run should demonstrate:

- Architecture artifact generation
- Tech lead backlog generation
- Verification that the tech lead created enough concrete tickets for all implementation workers
- Multiple implementation workers
- Validation that implementation workers created the files required by their assigned tickets
- Verification that required implementation files actually exist in `demo_repo/` after file application
- Multi-file project creation
- Test file generation and test command execution
- Feedback loop from failed tests back into repair implementation
- Documentation generation
- Deployment validation through checklist and GitHub Actions workflow
- Human approval before file edits and command execution
- Repeatable profile-based runs for model comparison
