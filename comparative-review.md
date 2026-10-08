# Comparative Review

## 1. Executive Summary

The two approaches implement different kinds of local multi-LLM workflows.

**Casper's approach** is primarily an interactive, human-controlled Open WebUI
workflow. Open WebUI provides model/provider selection, while Open Terminal
provides tool execution. The inspected project contains the resulting
FastAPI/SQLite task application and extensive validation documentation, but it
does not contain an executable multi-agent orchestration engine.

**Sebastian's approach** is an executable Python orchestration framework. It
calls Ollama endpoints directly, assigns staged roles to local models, writes
artifacts, generates project files, runs commands and tests, verifies required
files, and performs bounded repair attempts.

Casper's approach is simpler and more transparent for interactive local coding,
but the generated API currently contains an integration defect. Sebastian's
approach provides stronger workflow automation, staged handoffs, and repeatable
model profiles, but the generated application and deployment artifacts contain
several incomplete or unverified elements.

## 2. Architecture Comparison

| Area | Casper's approach | Sebastian's approach |
|---|---|---|
| Control plane/orchestration | Human-controlled Open WebUI/Open Terminal workflow. No executable orchestration runner, role scheduler, or model API client is present in the project folder. | Executable Python workflow in `src/local_multi_llm_workflow/workflow.py`. Stages include architecture, tech lead, implementation, verification, launch, testing, repair, documentation, deployment, and reporting. |
| Model selection/routing | Model/provider selection is performed through Open WebUI. The repository records endpoint evidence but does not implement routing. | YAML-driven model profiles in `configs/workflow.yaml`, loaded by `config.py` and used by `workflow.py`. |
| Local model endpoints | `http://127.0.0.1:11434` with `qwen3:8b`, and `http://127.0.0.1:11435` with `qwen2.5-coder:7b`. | Two configured endpoints on ports 11434 and 11435, with four selectable model profiles. One selected profile is used for all roles in a run. |
| Worker/role separation | Role separation is evidenced as part of the human workflow, but no worker scheduler or role implementation is present. | Explicit architect, tech lead, two implementers, tester, documenter, and deployment-validator roles. |
| Tool execution | Open Terminal is the tool-execution layer. | `Repository.run` uses `subprocess.run` for approved commands. |
| Artifact handoffs | Primarily human-mediated through Open WebUI and repository files. | Explicit artifact store, workflow state, generated file bundles, verification reports, quality reports, repair artifacts, and run summaries. |
| Human approval | Central to the workflow. | Configurable `ask_before_commands` and `ask_before_file_edits` controls. |
| Deployment topology | Single FastAPI container with SQLite file storage. | Intended React/client, Express/backend, MongoDB, and Nginx/API-gateway architecture. Actual `docker-compose.yml` defines only MongoDB and backend. |

Relevant references:

- `Mandatory 1 - Casper's approach/multi-endpoint-baseline.md`
- `Mandatory 1 - Casper's approach/docs/architecture.md`
- `Mandatory 1 - Casper's approach/app/main.py`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/workflow.py`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/config.py`
- `Mandatory 1 - sebastians approach/configs/workflow.yaml`

## 3. Functional Requirement Coverage

| Requirement | Casper's approach | Sebastian's approach |
|---|---|---|
| Architecture decomposition | **Strong** — `docs/architecture.md` defines client, FastAPI, service, repository, and database responsibilities. | **Strong/Partial** — generated architecture artifacts contain decomposition, contracts, topology, and ADR sections, but include components such as Nginx that are not implemented. |
| Interface contracts/OpenAPI | **Strong/Partial** — `docs/openapi.yaml` exists, but runtime validation and delete behavior differ from the contract. | **Partial** — Markdown interface examples exist, but no checked-in OpenAPI contract was found. |
| Deployment topology | **Strong/Partial** — Docker topology is implemented and documented, but CRUD validation failed. | **Partial** — compose and CI artifacts exist, but the documented frontend/Nginx topology is incomplete and validation did not complete successfully. |
| ADRs | **Strong** — `docs/adr/ADR-001-sqlite-for-local-demo.md` records the decision and alternatives. | **Partial** — ADR material is generated in the architecture artifact rather than maintained as separate ADR files. |
| Incremental tickets | **Strong** — `docs/tickets.md` defines scopes, dependencies, acceptance criteria, and definitions of done. | **Strong** — generated backlog tickets contain assigned workers, concrete file paths, acceptance criteria, and dependencies; the runner verifies them. |
| Multiple coding workers / parallel partitioning | **Weak** — evidenced as a human workflow, not encoded in this project. | **Strong** — implementation workers are executed through `ThreadPoolExecutor`. |
| Multi-file implementation | **Partial** — multiple application layers exist, but API/service integration is broken. | **Strong/Partial** — many files are generated and checked for existence, but key runtime files are missing or inconsistent. |
| Automated tests | **Partial** — 10 of 11 documented tests pass; the integration test fails. | **Weak/Partial** — generated tests exist, but `npm test` fails because Jest is unavailable; repairs did not resolve this. |
| Quality reporting | **Strong** — exact pass/fail and deployment results are recorded. | **Strong** — command output, failures, repair iterations, and npm audit findings are recorded. |
| README/setup documentation | **Strong** — README distinguishes intended and current behavior. | **Partial** — README and setup guide exist, but setup instructions do not fully match manifests and implementation. |
| Runbook | **Strong** — `docs/runbook.md` provides startup, verification, deployment, troubleshooting, and limitations. | **Weak/Partial** — README provides setup steps, but no equivalent detailed operational runbook was found. |
| Deployment validation | **Partial** — startup and health reportedly passed, but CRUD failed. | **Partial** — checklist and GitHub Actions validation exist, but recorded commands returned exit code 130 and deployment was not successfully demonstrated. |
| Git/reviewable changes | **Strong** — documentation records Git commits and reviewability. | **Partial** — artifacts and `git apply` are reviewable, but stage commits are disabled by default and the runner does not itself create commits. |
| Context/handoff management | **Weak/Partial** — human handoff through UI and files is evident but not encoded as a workflow engine. | **Strong** — workflow state, artifacts, repository snapshots, backlog context, and repair context are passed between stages. |
| Security | **Weak** — no authentication or authorization; local-only binding is recommended. | **Weak** — no authentication, broad CORS, no rate limiting, shell command execution, and reported npm vulnerabilities. |

## 4. Nonfunctional Comparison

### Setup complexity

Casper's approach requires a relatively small Python/FastAPI/Uvicorn
environment and optionally Docker. However, `pytest` is not declared in
`requirements.txt`, which weakens clean-environment reproducibility.

Sebastian's approach requires Python, PyYAML, Ollama, one or more local models,
two endpoints for the full comparison, Node dependencies, MongoDB, and
potentially Docker. It is more complex but supports repeated profile-based
experiments.

### Reproducibility

Sebastian's profile configuration and persisted artifacts provide stronger
procedural reproducibility. The same workflow can be rerun with different
profiles. Practical repeatability is still affected by nondeterministic model
output, interactive approvals, and external Ollama state.

Casper's approach is easier to understand and review, but exact workflow
reproduction depends on human Open WebUI and Open Terminal actions that are not
encoded in the repository.

### Controllability and transparency

Casper offers direct human control over model selection, tools, and generated
changes. Sebastian also offers approval gates, but has a more complex execution
path. Sebastian's artifact trail is stronger because each stage writes
structured outputs and reports.

### Failure isolation and recovery

Sebastian has explicit backlog verification, missing-file verification, bounded
repair iterations, and command-result recording. Casper relies more heavily on
human review and independent verification. Casper's quality report explicitly
demonstrates why this matters: the API route is disconnected from the
implemented service layer.

### Scalability and debugging

Sebastian scales better to additional roles and model profiles because roles,
endpoints, and controls are configuration-driven. Casper is easier to debug
for a human because the application is small, but the interactive workflow is
less formalized.

## 5. Multi-Endpoint Model Support

### Casper's approach

`multi-endpoint-baseline.md` records:

- `http://127.0.0.1:11434` with `qwen3:8b`
- `http://127.0.0.1:11435` with `qwen2.5-coder:7b`

The documented process uses Open WebUI for model/provider selection and Open
Terminal for tool execution. Endpoint 2 was independently tested through
Ollama's `/api/chat` endpoint. No executable routing code exists in the
inspected Casper project folder.

The workflow evidence also records that different local models showed
different reliability for structured tool calls. Therefore, model choice
affected whether tool-oriented operations were emitted in a usable form. This
is an observed property of the interactive workflow, not a capability
implemented by `app/main.py`.

### Sebastian's approach

Endpoint and model selection is implemented in `configs/workflow.yaml`. Four
profiles are defined:

- `qwen2_5_coder_3b` on `ollama_primary`
- `qwen2_5_coder_7b` on `ollama_primary`
- `qwen3_4b` on `ollama_primary`
- `llama3_1_8b` on `ollama_secondary`

`load_config` reads these mappings, and `_endpoint_url`, `_ask_role`, and
`_ask_file_role` use them to call Ollama. A selected profile applies one model
to all roles during a run. The implementation supports comparison across runs,
but not fine-grained per-role model routing within one configured run.

## 6. Failure Modes Observed or Evidenced

### Casper's approach

1. `app/main.py` defines a local stub `TaskService` instead of importing the
   implementation in `app/services/task_service.py`. As recorded in
   `docs/quality-report.md`, `POST /tasks` returns a FastAPI
   `ResponseValidationError`.
2. The test baseline is 10 passing tests, 1 failing test, and 1 warning.
3. The OpenAPI contract and runtime behavior differ for optional fields and
   missing-task deletion.
4. Docker startup and health validation succeeded, but CRUD failed before the
   real SQLite repository was reached.
5. `pytest` is absent from `requirements.txt`.
6. The SQLite path is hard-coded to `/workspace/data/tasks.db`.
7. There is no authentication, authorization, migration, backup,
   replication, or multi-instance coordination.

### Sebastian's approach

1. `backend/controllers/ticketController.js` calls `mongoose.model('Ticket')`,
   but no model definition or database connection is present in the inspected
   generated backend files.
2. The quality report records `npm test` failing because Jest was not
   recognized, and two repair iterations did not resolve it.
3. `client/src/TicketApp.js` uses Axios, but `client/package.json` does not
   declare Axios.
4. Backend tests expect a 200 JSON delete response, while the controller
   returns 204 with no body.
5. Controller methods have no explicit error handling, validation, or
   not-found handling.
6. The intended Nginx/frontend deployment topology is not represented in
   `docker-compose.yml`.
7. The run summary records deployment-related commands returning exit code 130.
8. The quality report records four npm audit vulnerabilities: one moderate and
   three high.

The Sebastian workflow itself has meaningful recovery and safety mechanisms:
HTTP/URL errors are surfaced in `llm.py`, generated paths are restricted to the
target repository, file and command approval gates exist, backlog verification
is explicit, implementation files are checked after application, and quality
repair is bounded and recorded.

## 7. Key Architectural Difference

Casper's approach is an interactive Open WebUI workflow:

```text
Human
  -> Open WebUI model/provider selection
  -> Open Terminal tool execution
  -> Human review and verification
  -> Generated repository
```

Its strength is direct human control. An operator can change models
interactively, inspect outputs, retry tool calls, and independently validate
generated work. Its weakness is that the workflow is not fully encoded as
reproducible program logic.

Sebastian's approach is a programmatic staged workflow:

```text
Python runner
  -> Architect
  -> Tech lead/backlog verifier
  -> Parallel implementers
  -> File verification
  -> Tester
  -> Repair loop
  -> Documenter
  -> Deployment validator
  -> Artifact/run summary
```

Programmatic orchestration provides stronger automation, repeatability, worker
partitioning, and machine-readable handoffs. It also introduces more
operational complexity and more interfaces where generated artifacts can be
formally accepted while remaining nonfunctional.

## 8. Recommendation

| Use case | Better fit |
|---|---|
| Interactive local coding with a human | Casper's approach: simpler, direct UI control, easy model switching, and visible tool execution. |
| Reproducible automated coding workflows | Sebastian's approach: executable stages, profiles, artifacts, verification, and bounded repair. |
| Experimenting with different local models | Sebastian's approach for repeatable profile runs; Casper's approach for interactive qualitative comparison of tool-call reliability. |
| Controlled multi-worker development | Sebastian's approach: explicit worker roles, ticket assignment, parallel generation, and file verification. |
| CI/headless execution | Sebastian's approach in principle, after repairing missing dependencies, incomplete deployment wiring, and interactive approval assumptions. |
| Ease of setup for a student/developer | Casper's approach: substantially smaller runtime and dependency surface. |

Neither approach is universally superior. Casper is better as a human-in-the-loop
local coding experiment. Sebastian is better as a research prototype for
explicit orchestration and repeatable multi-agent workflow evaluation,
provided generated project correctness is independently verified.

## 9. Evidence References

### Casper's approach

- `Mandatory 1 - Casper's approach/README.md`
- `Mandatory 1 - Casper's approach/app/main.py`
- `Mandatory 1 - Casper's approach/app/services/task_service.py`
- `Mandatory 1 - Casper's approach/app/repositories/sqlite_repo.py`
- `Mandatory 1 - Casper's approach/docs/architecture.md`
- `Mandatory 1 - Casper's approach/docs/openapi.yaml`
- `Mandatory 1 - Casper's approach/docs/quality-report.md`
- `Mandatory 1 - Casper's approach/docs/tickets.md`
- `Mandatory 1 - Casper's approach/docs/runbook.md`
- `Mandatory 1 - Casper's approach/docs/adr/ADR-001-sqlite-for-local-demo.md`
- `Mandatory 1 - Casper's approach/multi-endpoint-baseline.md`
- `Mandatory 1 - Casper's approach/Dockerfile`

### Sebastian's approach

- `Mandatory 1 - sebastians approach/README.md`
- `Mandatory 1 - sebastians approach/SETUP_GUIDE.md`
- `Mandatory 1 - sebastians approach/configs/workflow.yaml`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/workflow.py`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/config.py`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/llm.py`
- `Mandatory 1 - sebastians approach/src/local_multi_llm_workflow/repository.py`
- `Mandatory 1 - sebastians approach/demo_repo/README.md`
- `Mandatory 1 - sebastians approach/demo_repo/docker-compose.yml`
- `Mandatory 1 - sebastians approach/demo_repo/backend/controllers/ticketController.js`
- `Mandatory 1 - sebastians approach/demo_repo/client/src/TicketApp.js`
- `Mandatory 1 - sebastians approach/demo_repo/client/package.json`
- `Mandatory 1 - sebastians approach/artifacts/qwen2_5_coder_7b/architecture/architecture.md`
- `Mandatory 1 - sebastians approach/artifacts/qwen2_5_coder_7b/quality/quality-report.md`
- `Mandatory 1 - sebastians approach/artifacts/qwen2_5_coder_7b/run-summary.md`

## Report-ready Comparison

Casper's and Sebastian's approaches represent two different interpretations of
a local multi-LLM coding workflow. Casper's approach is an interactive
Open WebUI-based process in which a human selects local models and providers,
uses Open Terminal as the execution layer, reviews generated changes, and
independently verifies the result. The repository contains the resulting
FastAPI/SQLite task application and extensive validation documentation, but it
does not contain an executable orchestration engine. Its architecture is
intentionally small: FastAPI routes should call a service layer, which should
call a SQLite repository. This makes the system easy to understand and
suitable for interactive experimentation with different local models.

However, the implementation does not fully realize its intended architecture.
`app/main.py` defines a local stub `TaskService` instead of importing the
implemented service, so the health endpoint works while task creation fails.
The quality report records 10 passing tests and one failing integration test,
and Docker validation reached startup and health verification but not
successful CRUD execution. The OpenAPI contract, runtime validation, and
delete behavior also differ in places. Casper's workflow demonstrates the
importance of human review and independent verification, especially because
different local models showed different reliability for structured tool calls.

Sebastian's approach implements the workflow itself as a Python program. It
calls Ollama's `/api/chat` endpoint, supports two configured endpoints and four
model profiles, and assigns explicit roles to an architect, tech lead, two
implementation workers, tester, documenter, and deployment validator. The
workflow creates architecture and backlog artifacts, verifies ticket coverage,
runs implementation workers in parallel, applies their file bundles only after
approval, checks required files on disk, runs generated tests, and performs
bounded repair iterations. This provides stronger artifact handoffs,
reproducibility across model profiles, and scalability to additional workers
or endpoints. It is therefore a stronger orchestration research prototype
than Casper's repository-level implementation.

Nevertheless, Sebastian's generated application shows the risks of automated
generation. The quality report records that `npm test` failed because Jest was
unavailable, and two repair iterations did not resolve the issue. The backend
controller references a Mongoose `Ticket` model, but the inspected project
does not define the model or establish a database connection. The client
imports Axios although its package manifest does not declare it, and the tests
expect a different delete response from the controller. The documented Nginx
and frontend deployment topology is also not represented by the actual Docker
Compose file. Security is weak in both approaches: neither implements
authentication or authorization. Sebastian additionally permits approved shell
commands through `subprocess.run(..., shell=True)` and reports four npm audit
vulnerabilities.

Consequently, Casper's approach is better for interactive local coding, human
control, and ease of setup. Sebastian's approach is better for reproducible
automated workflows, explicit multi-worker partitioning, artifact traceability,
and controlled model comparison. Neither should be judged solely by
documentation: Casper's implementation defect and Sebastian's incomplete
generated project demonstrate that workflow claims must be checked against
executable behavior and independently recorded results.
