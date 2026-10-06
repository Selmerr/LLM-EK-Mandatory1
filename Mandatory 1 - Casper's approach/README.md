# Local Task API Demo

A small FastAPI REST API for managing tasks. This repository is part of a
local Open WebUI multi-LLM coding workflow evaluation and is intended for
local development, API experimentation, and deployment-artifact validation.

## Status

This is a local evaluation/demo application, not a production-ready service.

The independently verified test result supplied for this repository is:

- 11 tests collected
- 10 passed
- 1 failed
- 1 warning

The failed integration test exposes a known TaskService wiring defect described
in [Known limitations](#known-limitations).

No tests or Docker validation are claimed as part of this documentation work.

## Architecture

### Intended architecture

The intended request flow is:

```text
HTTP client
    -> FastAPI routes
    -> TaskService
    -> SQLiteRepo
    -> SQLite database file
```

The intended components are:

- `app/main.py`: FastAPI application and HTTP routes
- `app/models/task.py`: Pydantic request and response models
- `app/services/task_service.py`: SQLite-backed task service
- `app/repositories/sqlite_repo.py`: SQLite persistence

The API contract is documented in
[docs/openapi.yaml](docs/openapi.yaml).

### Current implementation behavior

The current `app/main.py` does not use the intended service-layer wiring. It
defines and injects a local stub `TaskService` instead of importing the real
implementation from `app/services/task_service.py`.

Consequently, the process can start and the health endpoint can respond while
task CRUD operations do not exercise the intended SQLite-backed service.

The repository implementation uses the hard-coded database path
`/workspace/data/tasks.db`.

## Prerequisites

- Python 3.12 or a compatible Python version
- `pip`
- Docker, if using the container workflow
- A shell capable of running the commands below

`pytest` is used by the existing tests but is not declared in
`requirements.txt`. A clean environment therefore needs a separately available
pytest installation to reproduce the test suite.

## Local setup

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the declared application dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the API

From the repository root:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API is then available at `http://127.0.0.1:8000`.

FastAPI's interactive documentation is normally available at
`http://127.0.0.1:8000/docs`. The checked-in contract is
[docs/openapi.yaml](docs/openapi.yaml).

## Health check

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"healthy","message":"Task API is running"}
```

This verifies the health route only. It does not verify task CRUD.

## API usage

The checked-in API contract defines these endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Return service health |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks |
| GET | `/tasks/{id}` | Get one task |
| PUT | `/tasks/{id}` | Update one task |
| DELETE | `/tasks/{id}` | Delete one task |

The current request models require all task fields below, including
`description` and `due_date`, even where the OpenAPI document describes them as
optional.

Create a task:

```powershell
curl.exe -X POST http://127.0.0.1:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Review workflow","description":"Check the local demo","status":"pending","priority":1,"due_date":"2026-12-31T00:00:00Z"}'
```

List tasks:

```powershell
curl.exe http://127.0.0.1:8000/tasks
```

Get a task:

```powershell
curl.exe http://127.0.0.1:8000/tasks/<task-id>
```

Update a task:

```powershell
curl.exe -X PUT http://127.0.0.1:8000/tasks/<task-id> `
  -H "Content-Type: application/json" `
  -d '{"title":"Review workflow","description":"Updated local demo task","status":"in-progress","priority":2,"due_date":"2026-12-31T00:00:00Z"}'
```

Delete a task:

```powershell
curl.exe -i -X DELETE http://127.0.0.1:8000/tasks/<task-id>
```

These commands describe the existing contract and intended requests. They have
not been validated as a successful end-to-end CRUD workflow because of the
known TaskService integration defect.

## Testing

Run the tests from an environment with pytest installed:

```powershell
python -m pytest
```

The independently verified result supplied for this repository is:

```text
11 tests collected
10 passed
1 failed
1 warning
```

The failed integration test is caused by `app/main.py` using a local stub
`TaskService` instead of the implementation in
`app/services/task_service.py`. This documentation does not repair that defect.

Because pytest is not declared in `requirements.txt`, the declared dependency
installation alone does not guarantee that the test command is available.

## Docker build and run

Build the image from the repository root:

```powershell
docker build -t local-task-api .
```

Create a host data directory and run the container detached:

```powershell
New-Item -ItemType Directory -Force .\data

docker run -d --name local-task-api `
  -p 127.0.0.1:8001:8000 `
  -v "${PWD}\data:/workspace/data" `
  local-task-api
```

The container is intended to be available at
`http://127.0.0.1:8001`.

The Dockerfile creates `/workspace/data`, matching the application's current
hard-coded database path `/workspace/data/tasks.db`. The bind mount is
recommended when data should survive container replacement.

Docker build, startup, health, and CRUD behavior have not been validated as
part of this documentation work.

## Known limitations

- `app/main.py` currently defines and injects a local stub `TaskService` rather
  than importing the real implementation from
  `app/services/task_service.py`.
- The known defect means task operations do not exercise the intended
  SQLite-backed implementation.
- The independently verified test result is 11 collected, 10 passed, 1 failed,
  and 1 warning.
- The SQLite path is hard-coded to `/workspace/data/tasks.db`.
- Local execution and deployment must provide that directory and make it
  writable.
- SQLite is intended for this single-node local demo, not for high-concurrency
  or production workloads.
- There is no authentication, authorization, migration system, backup system,
  replication, or multi-instance coordination.
- The OpenAPI document and runtime behavior are not perfectly aligned in every
  validation and error case.
- `pytest` is not declared in `requirements.txt`, limiting clean-environment
  test reproducibility.
- Docker deployment and API CRUD have not been validated by this documentation
  work.

## Security considerations

- Bind local development to `127.0.0.1` unless external access is explicitly
  required.
- Do not expose this unauthenticated API to an untrusted network.
- Restrict permissions on the host directory mounted at `/workspace/data`.
- Do not place secrets in task data, shell history, image layers, or committed
  configuration.
- Treat container logs and SQLite files as potentially sensitive.
- Use a production database, authentication, authorization, TLS termination,
  backups, and operational monitoring before considering a production design.
