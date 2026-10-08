# Local Task API Runbook

This runbook covers local execution and single-container deployment
procedures for the FastAPI task demo. The procedures are documentation only;
Docker startup and API CRUD have not been validated as part of this work.

## Startup procedure

1. Change to the repository root.
2. Confirm Python and `pip` are available.
3. Create and activate an isolated environment if needed:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the declared dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the API:

   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

The declared requirements do not include pytest. Install or otherwise provide
pytest separately before running the test suite.

## Health verification

In a second terminal:

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

Confirm an HTTP 200 response and this JSON body:

```json
{"status":"healthy","message":"Task API is running"}
```

A passing health check verifies process routing only. It does not verify task
CRUD or SQLite persistence.

## Basic API verification

The checked-in contract is [openapi.yaml](openapi.yaml). The current request
models require all fields in this payload:

```powershell
curl.exe -X POST http://127.0.0.1:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{"title":"Runbook task","description":"Smoke test","status":"pending","priority":1,"due_date":"2026-12-31T00:00:00Z"}'
```

If creation succeeds, use the returned ID to try:

```powershell
curl.exe http://127.0.0.1:8000/tasks

curl.exe http://127.0.0.1:8000/tasks/<task-id>

curl.exe -X PUT http://127.0.0.1:8000/tasks/<task-id> `
  -H "Content-Type: application/json" `
  -d '{"title":"Updated runbook task","description":"Updated smoke test","status":"complete","priority":2,"due_date":"2026-12-31T00:00:00Z"}'

curl.exe -i -X DELETE http://127.0.0.1:8000/tasks/<task-id>
```

The current application wiring contains a known TaskService integration defect,
so task-operation smoke tests may fail even when the process and health check
are available.

## Testing

Run the existing tests from an environment with pytest installed:

```powershell
python -m pytest
```

The independently verified baseline supplied for this repository is:

- 11 tests collected
- 10 passed
- 1 failed
- 1 warning

The failure is caused by `app/main.py` using a local stub `TaskService` rather
than the implementation in `app/services/task_service.py`. Do not treat a
passing health check as evidence that task CRUD is functional.

## Docker deployment

Build the image from the repository root:

```powershell
docker build -t local-task-api .
```

Create a host directory for persistence:

```powershell
New-Item -ItemType Directory -Force .\data
```

Start the container detached:

```powershell
docker run -d --name local-task-api `
  -p 127.0.0.1:8001:8000 `
  -v "${PWD}\data:/workspace/data" `
  local-task-api
```

Use `http://127.0.0.1:8001` for subsequent health and API checks.

The Dockerfile creates `/workspace/data`, and the application currently opens
`/workspace/data/tasks.db`. The bind mount is needed if the SQLite file should
survive container replacement.

Docker build, startup, health, and CRUD behavior have not been run or validated
as part of this documentation work.

## Docker logs

For a snapshot of container output:

```powershell
docker logs local-task-api
```

For live output:

```powershell
docker logs -f local-task-api
```

Review startup errors before attempting API verification.

## Stopping and removing the container

For a running named container:

```powershell
docker stop local-task-api
docker rm local-task-api
```

Do not remove the host `data` directory without first confirming whether its
SQLite file must be retained.

## Troubleshooting

### Port 8001 is unavailable

The default container validation mapping uses host port 8001 to avoid the
known Open Terminal host-port conflict. Check which process or container owns
the port, stop the conflict, or choose another explicitly recorded host port.

For example:

```powershell
docker run -d --name local-task-api `
  -p 127.0.0.1:8002:8000 `
  -v "${PWD}\data:/workspace/data" `
  local-task-api
```

Then use `http://127.0.0.1:8002`.

### The container exits immediately

Inspect the logs:

```powershell
docker logs local-task-api
```

Confirm that the image was built from the repository root and that the image
contains the `app` package.

### Health succeeds but task requests fail

This is consistent with the known integration defect. `app/main.py` creates a
local stub `TaskService` whose methods are not connected to the real SQLite
service. Do not silently classify this as a database or networking failure.

### SQLite errors or missing data

The repository uses the hard-coded path `/workspace/data/tasks.db`. Confirm
that `/workspace/data` exists and is writable. For Docker, confirm that a bind
mount or named volume targets `/workspace/data`.

Without external storage, data in a removed container is not expected to
persist.

## SQLite/database considerations

- SQLite is file-based and requires no separate database server.
- SQLite is selected for a single local node and low-volume evaluation.
- It is not an appropriate basis for high-concurrency or production workloads.
- Back up the database file before destructive testing if it contains data.
- The repository provides no migrations, automated backups, replication, or
  multi-instance coordination.
- Filesystem permissions for the database directory must be reviewed.

## Known TaskService integration defect

`app/main.py` currently defines and injects a local stub `TaskService` instead of
importing the real implementation from `app/services/task_service.py`.

This is an application defect intentionally documented here rather than fixed
as part of the deployment artifacts. The independently verified baseline is
10 passing tests and 1 failing test out of 11, with 1 warning.

## Deployment limitations

- No authentication or authorization is implemented.
- The API is unauthenticated and should remain local unless additional controls
  are added.
- The SQLite location is hard-coded and requires deployment-specific writable
  storage.
- There is no TLS, reverse proxy configuration, health-based orchestration,
  backup automation, migration process, or observability setup.
- A process-level health check does not establish that task CRUD works.
- `pytest` is not declared in `requirements.txt`, so the declared dependency
  installation is insufficient by itself for reproducible test execution.
