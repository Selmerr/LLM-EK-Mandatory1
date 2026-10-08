# Incremental Ticket Plan

## Purpose

This document records the incremental work plan used to partition the Task API implementation across coding workers. Each ticket has an explicit file scope, acceptance criteria, Definition of Done, and dependency relationship.

## TSK-001 - Architecture and API Contract

**Owner:** Architecture / Contract Worker

**Scope:**

* `docs/architecture.md`
* `docs/openapi.yaml`

**Dependencies:** None.

**Acceptance Criteria:**

* Component responsibilities are documented.
* Data flow between API, service, repository, and database is documented.
* Deployment topology and constraints are documented.
* REST endpoints and request/response contracts are documented in OpenAPI.
* API error responses are specified.

**Definition of Done:**

* Architecture document exists and describes the intended component boundaries.
* OpenAPI document defines the health and task CRUD endpoints.
* No application implementation files are modified.

## TSK-002 - Task API Implementation

**Owner:** Implementation Worker

**Scope:**

* `app/main.py`
* `app/models/task.py`
* `app/services/task_service.py`
* `app/repositories/sqlite_repo.py`
* `requirements.txt`

**Dependencies:** TSK-001.

**Acceptance Criteria:**

* FastAPI application exposes the planned task endpoints.
* Pydantic models represent task creation, updates, and responses.
* Service layer contains task business operations.
* SQLite repository provides persistent CRUD storage.
* Database uses the documented local path.

**Definition of Done:**

* Implementation files are present.
* Python syntax checks pass.
* Changes are committed to Git.
* Integration between the API and service layer is subsequently verified by testing.

## TSK-003 - Automated Testing

**Owner:** Test Worker

**Scope:**

* `tests/test_api.py`
* `tests/test_models.py`

**Dependencies:** TSK-001 and TSK-002.

**Acceptance Criteria:**

* Model validation tests cover valid and invalid inputs.
* API tests cover health, task creation, and missing-task behavior.
* Tests detect integration failures between API and service layers.
* Test results are recorded.

**Definition of Done:**

* Test files exist and are reviewed independently.
* Tests are executed in the available container environment.
* Actual pass/fail results are recorded rather than relying on worker claims.
* Known failures and warnings are documented.

## TSK-004 - Documentation and Deployment Validation

**Owner:** Documentation / Deployment Worker

**Scope:**

* `README.md`
* `docs/runbook.md`
* `docs/adr/ADR-001-sqlite-for-local-demo.md`
* `Dockerfile`
* `deployment/checklist.md`

**Dependencies:** TSK-001, TSK-002, and TSK-003.

**Acceptance Criteria:**

* README documents setup and execution.
* Runbook documents operational steps and troubleshooting.
* ADR records the SQLite decision and alternatives.
* Dockerfile provides a reproducible container build.
* Deployment checklist defines build, startup, health, and security validation.

**Definition of Done:**

* Documentation is committed to Git.
* Docker image builds successfully.
* Container starts successfully.
* Health endpoint is validated.
* Host binding is checked for local-only exposure.
* Deployment limitations are recorded.

## Cross-Worker Integration Finding

Independent verification identified an integration defect after TSK-002 and TSK-003:

`app/main.py` contains a local `TaskService` stub rather than importing the implemented `app.services.task_service.TaskService`.

Consequently, the `/health` endpoint succeeds, but task creation fails with a FastAPI `ResponseValidationError`.

This finding demonstrates why worker completion claims require independent integration testing before the workflow can be considered complete.

## Reproducibility and Review

Each completed ticket is represented by a Git commit where applicable. File ownership and scope were used to reduce accidental overlap between workers.

The workflow used human approval before controlled edits and independent verification after worker-generated changes.
