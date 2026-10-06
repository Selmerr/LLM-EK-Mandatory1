# Open WebUI Multi-LLM Coding Workflow — Approach

## 1. Purpose

This project evaluates a local multi-LLM coding workflow using **Open WebUI as the primary orchestration and user-control interface**, with **Ollama providing multiple local model endpoints** and **Open Terminal providing controlled terminal access to the coding workspace**.

The goal was to demonstrate that multiple local language models can be used for different software-engineering responsibilities without manually rewiring the workflow between models.

The approach deliberately differs from a custom Python orchestration workflow. Instead of building a bespoke controller, the workflow uses Open WebUI's existing model selection, connection management, agent/tool integration, conversation history, and approval-oriented interaction.

---

## 2. High-Level Architecture

```text
                           ┌───────────────────────┐
                           │      Open WebUI       │
                           │                       │
                           │  Model selection      │
                           │  Conversations        │
                           │  Agent/tool control   │
                           │  User approval        │
                           └───────────┬───────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
                    ▼                                     ▼
          ┌───────────────────┐                 ┌───────────────────┐
          │   Ollama #1       │                 │   Ollama #2       │
          │ 127.0.0.1:11434   │                 │ 127.0.0.1:11435   │
          │                   │                 │                   │
          │ qwen3:8b          │                 │ qwen2.5-coder:7b  │
          └───────────────────┘                 └───────────────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │   Open Terminal  │
                              │                  │
                              │ Controlled tool  │
                              │ execution layer  │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │     Git repo     │
                              │                  │
                              │ Task API demo    │
                              └──────────────────┘
```

The important architectural property is that **model selection happens at the Open WebUI level**. The coding workspace remains the same regardless of which local model is selected.

---

## 3. Local Model and Endpoint Strategy

Two separate Ollama endpoints were configured:

| Endpoint          | Model              | Intended responsibility                                    |
| ----------------- | ------------------ | ---------------------------------------------------------- |
| `127.0.0.1:11434` | `qwen3:8b`         | Architecture, technical leadership, implementation, review |
| `127.0.0.1:11435` | `qwen2.5-coder:7b` | Coding-oriented worker                                     |

The second Ollama instance was started with a different `OLLAMA_HOST` value:

```powershell
$env:OLLAMA_HOST="127.0.0.1:11435"
ollama serve
```

The endpoints were then registered as separate Ollama connections in Open WebUI.

This provides configurable multi-endpoint routing without changing application code or creating separate repositories for different models.

A direct API test against endpoint #2 returned the expected marker:

```text
ENDPOINT_2_OK
```

with HTTP 200 and a completed response.

The local machine used for the evaluation has approximately 32 GB of RAM and an NVIDIA RTX 5070 Ti with approximately 16 GB of VRAM available to Ollama.

---

## 4. Why Open WebUI Was Used

The primary reason for selecting Open WebUI was to evaluate a workflow that relies on an existing local AI interface rather than implementing a custom orchestration program.

Open WebUI provides the control plane for:

* selecting local models;
* configuring multiple Ollama connections;
* maintaining separate conversations;
* defining model presets;
* integrating terminal/tool capabilities;
* reviewing proposed actions before allowing changes;
* keeping the human operator in the workflow.

This makes the approach relatively easy to understand and reproduce.

The trade-off is that Open WebUI does not automatically provide the same deterministic stage orchestration or artifact management that a purpose-built Python runner can provide. Some workflow guarantees therefore depend on prompts, model behavior, Git discipline, and human verification.

---

## 5. Open Terminal Integration

Open Terminal was added as the tool/agent execution layer.

It was run as a separate Docker container and connected to Open WebUI. The coding workspace was mounted into the container at:

```text
/workspace
```

The terminal environment was resource constrained:

```text
Memory: 2 GB
CPUs:   2
```

The terminal API was protected with an API key.

The coding models could therefore inspect and modify the Git repository through the terminal integration rather than receiving direct unrestricted access to the Windows host.

The terminal also exposed an OpenAPI/Swagger interface at its local `/docs` endpoint, which provided evidence that the terminal service was running and exposed its API contract.

---

## 6. Model Roles

The workflow used separate conversations for different software-engineering responsibilities.

### Architecture / Technical Lead

The architecture worker was responsible for:

* decomposing the problem;
* defining component responsibilities;
* producing the initial architecture;
* defining the API contract;
* identifying deployment constraints;
* creating an Architecture Decision Record;
* producing incremental implementation tickets.

The resulting design separated:

```text
FastAPI
    ↓
TaskService
    ↓
SQLiteRepo
    ↓
SQLite database
```

### Implementation Worker A

The first implementation worker owned the API/application layer:

```text
app/main.py
app/models/task.py
requirements.txt
```

It implemented the initial FastAPI routes and Pydantic models.

### Implementation Worker B

The second implementation worker owned the persistence/business layer:

```text
app/services/task_service.py
app/repositories/sqlite_repo.py
```

This demonstrated partitioning of implementation work across multiple coding workers while keeping explicit file ownership boundaries.

### Testing Worker

A separate worker was tasked with producing:

```text
tests/test_api.py
tests/test_models.py
```

The worker's output was independently inspected and tested rather than being accepted solely on the basis of its completion message.

This became an important part of the evaluation because the first generated test implementation did not match the actual application interfaces.

### Documentation / Deployment

Documentation and deployment artifacts were produced separately, with a restricted file scope covering:

```text
README.md
docs/runbook.md
docs/adr/ADR-001-sqlite-for-local-demo.md
Dockerfile
deployment/checklist.md
```

The documentation phase explicitly avoided changing the known application defect.

---

## 7. Incremental Work and File Ownership

The workflow used explicit tickets to make parallel work reviewable.

The main tickets were:

| Ticket  | Responsibility                | Dependencies              |
| ------- | ----------------------------- | ------------------------- |
| TSK-001 | Architecture and API contract | None                      |
| TSK-002 | Application implementation    | TSK-001                   |
| TSK-003 | Automated tests               | TSK-001, TSK-002          |
| TSK-004 | Documentation and deployment  | TSK-001, TSK-002, TSK-003 |

Each ticket defined:

* scope;
* owned files;
* dependencies;
* acceptance criteria;
* Definition of Done.

This reduced the risk of multiple workers editing the same files simultaneously and made the resulting Git history easier to review.

---

## 8. Human Control and Approval

The workflow was intentionally operated with a human in the loop.

A representative control test asked the model to:

1. inspect the repository;
2. propose an exact change;
3. show the expected diff;
4. stop and wait for approval.

The model stopped before editing.

After approval, it made the change, and the resulting Git diff was independently inspected.

The resulting commit was:

```text
10dc6ae docs: add task api purpose
```

This demonstrates a **plan → approval → edit → verify → commit** workflow.

Git was used as the reproducibility and review mechanism throughout the project.

---

## 9. Reproducibility Strategy

The repository was initialized with Git before implementation work began.

The work was committed incrementally:

```text
e97acdd chore: initialize task API demo
10dc6ae docs: add task api purpose
47d5c78 docs: add architecture and API contract
441ca81 feat: add task API application layer
59caea3 feat: add task service and sqlite repository
508b105 docs: add runbook deployment and test artifacts
a277088 docs: add quality and deployment report
6518090 docs: add incremental ticket plan
```

This gives the evaluation a reviewable history rather than only a final repository state.

The workflow also used explicit file scopes and independent verification so that worker claims could be compared with the actual repository state.

---

## 10. Testing and Independent Verification

A key principle of the evaluation was:

> Worker completion messages were treated as claims, not as test evidence.

This was important because several worker outputs were initially incorrect or incomplete.

The final independently executed test run was:

```text
11 tests collected
10 passed
1 failed
1 warning
```

The failing test exposed a real integration defect.

`app/main.py` contains a local `TaskService` stub, while the real implementation exists in:

```text
app/services/task_service.py
```

The API routes therefore use the local stub instead of the real service implementation.

The failing `POST /tasks` test produced a FastAPI response validation error because the stub returned an invalid value.

This was valuable evidence because the multi-worker workflow successfully produced independently detectable cross-worker integration problems.

---

## 11. Deployment Validation

The application was packaged into a Docker image using the generated Dockerfile.

The image was successfully built as:

```text
local-task-api:latest
```

The container was started with a localhost-only host binding:

```text
127.0.0.1:8001:8000
```

This was intentional because the evaluation requires that local model endpoints and related services not be unnecessarily exposed publicly.

The container started successfully and the health endpoint returned:

```json
{
  "status": "healthy",
  "message": "Task API is running"
}
```

However, the task creation endpoint failed with HTTP 500 because of the known `TaskService` integration defect.

The SQLite database was consequently not created during the failed POST request.

The deployment validation therefore demonstrates both successful infrastructure startup and a meaningful application-level failure.

---

## 12. Security Approach

The model endpoints were bound to loopback addresses:

```text
127.0.0.1:11434
127.0.0.1:11435
```

This prevents the Ollama endpoints from being intentionally exposed on the LAN by the configuration used for the evaluation.

Open Terminal was protected using an API key.

The demo Task API container was also bound to:

```text
127.0.0.1:8001
```

rather than all host interfaces.

The Task API itself does not implement user authentication or authorization. This is documented as a limitation of the demonstration application rather than presented as a production security design.

---

## 13. Important Failure Modes Discovered

The evaluation deliberately recorded failures rather than hiding them.

### Model loading failure

The initially selected `gpt-oss:20b` model failed to load in Ollama with a GGUF tensor metadata/size overflow error.

This established that model compatibility/loading can be an independent failure point before Open WebUI is involved.

The model was removed and `qwen3:8b` was used successfully instead.

### Model/tool compatibility

`qwen2.5-coder:7b` did not reliably produce the structured Open Terminal tool calls expected by the configured workflow. In some interactions it produced plain-text JSON instead.

`qwen3:8b` was more reliable for the Open Terminal interaction in this setup.

This demonstrates that multi-model routing does not guarantee equivalent agent/tool behavior across models.

### Context limitation

The initial Open WebUI model preset used a context size that was too small for the tool definitions and conversation context.

Increasing the qwen3 preset to:

```text
16384
```

resolved the observed context truncation problem.

### Incorrect generated artifacts

The initial OpenAPI output required independent correction.

The initial testing worker also produced tests that did not match the actual repository.

These incidents reinforce the need for artifact inspection and executable verification.

### Integration defect

The final application has a known mismatch between the API layer and the real service implementation.

This defect was intentionally documented rather than silently fixed after the evaluation evidence had been collected.

---

## 14. Strengths of the Approach

The Open WebUI approach demonstrated:

* two independently configured local LLM endpoints;
* model switching without application rewiring;
* multiple coding workers;
* explicit worker responsibilities;
* incremental tickets;
* file-level ownership boundaries;
* human approval before edits;
* Git-based reviewability;
* terminal/tool integration;
* automated testing;
* Docker packaging;
* deployment validation;
* documented failure modes;
* reproducible evidence.

It also keeps the architecture relatively understandable for a human operator.

---

## 15. Limitations

The approach is less deterministic than a purpose-built orchestration program.

Open WebUI coordinates the interaction, but it does not automatically guarantee:

* that a worker obeys its requested file scope;
* that generated artifacts are correct;
* that a model produces valid tool calls;
* that one worker's implementation integrates with another worker's implementation;
* that tests claimed by a worker were actually executed;
* that all workflow stages execute in a fixed deterministic sequence.

The evaluation therefore depends significantly on:

1. explicit prompts;
2. constrained file ownership;
3. Git;
4. independent verification;
5. human approval;
6. executable tests.

This is an important distinction from a custom workflow runner, where more of the sequencing and artifact handoff can be encoded directly in software.

---

## 16. Overall Evaluation Position

The Open WebUI approach is best viewed as a **human-controlled local multi-LLM development environment** rather than a fully deterministic software-engineering orchestrator.

Its main advantage is simplicity and usability: models, endpoints, conversations, and tools can be managed through a single interface while keeping the underlying models local.

Its main weakness is that correctness depends on model behavior and verification discipline. The evaluation found several examples where worker claims did not correspond to correct repository state.

For a developer or small team that wants an accessible local multi-model coding workflow, this approach is practical and easy to demonstrate.

For a highly reproducible CI-style workflow requiring deterministic stage ordering, strict artifact contracts, automated retries, and machine-enforced worker boundaries, a custom orchestration layer would provide stronger guarantees.

The most appropriate conclusion is therefore not that one architecture is universally better, but that the Open WebUI approach provides a strong **interactive and human-in-the-loop workflow**, while a custom runner provides stronger **programmatic orchestration and reproducibility guarantees**.
