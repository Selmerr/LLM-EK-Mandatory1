# Local Deployment Validation Checklist

Use this checklist for local or single-container validation of the Task API.
Checking an item means that the operator performed the check; the checklist
itself does not claim that these checks have already passed.

## Prerequisites

- [ ] Repository is present at the intended local path.
- [ ] Python and `pip` are available.
- [ ] Docker is available if container validation is required.
- [ ] Host port 8001 is available, or an alternate host port is selected.
- [ ] A writable host directory is available for SQLite persistence when using
      Docker.
- [ ] pytest is available separately if tests are to be run; it is not declared
      in `requirements.txt`.

## Repository and Git state

- [ ] Confirm the intended branch and commit.
- [ ] Review `git status --short`.
- [ ] Confirm no unreviewed application changes are being included.
- [ ] Confirm `requirements.txt` is the dependency source for the application.
- [ ] Confirm `docs/openapi.yaml` is the API contract being used for reference.
- [ ] Confirm the known TaskService integration defect is understood and
      documented.

## Dependency installation

- [ ] Create or select an isolated Python environment.
- [ ] Install the declared dependencies:

      python -m pip install -r requirements.txt

- [ ] Confirm FastAPI and Uvicorn are importable from that environment.
- [ ] If running tests, confirm pytest is installed separately.

## Docker build

- [ ] Build from the repository root:

      docker build -t local-task-api .

- [ ] Confirm the build completes without errors.
- [ ] Confirm the image contains `app/`.
- [ ] Confirm the image uses the existing `requirements.txt`.
- [ ] Confirm the image creates `/workspace/data`.
- [ ] Confirm the image exposes port 8000.
- [ ] Do not treat a successful image build as evidence that API CRUD works.

## Container startup

- [ ] Create a host persistence directory:

      New-Item -ItemType Directory -Force .\data

- [ ] Start the validation container detached using the default host port 8001:

      docker run -d --name local-task-api -p 127.0.0.1:8001:8000 -v "${PWD}\data:/workspace/data" local-task-api

- [ ] Confirm the container remains running.
- [ ] Confirm `/workspace/data` is writable by the container process.
- [ ] Record that startup validation was actually performed.

## Port availability

- [ ] Confirm host port 8001 is not occupied.
- [ ] The default mapping is `127.0.0.1:8001:8000` to avoid the known
      Open Terminal host-port conflict.
- [ ] If using another host port, record the mapping.
- [ ] Use the mapped host port for all subsequent checks.

## Health check

- [ ] Request `GET /health`:

      curl.exe -i http://127.0.0.1:8001/health

- [ ] Confirm HTTP 200.
- [ ] Confirm the body contains `status: healthy`.
- [ ] Confirm the body contains `Task API is running`.
- [ ] Do not treat a passing health check as evidence that task CRUD works.

## API smoke testing

- [ ] Submit a complete `POST /tasks` payload matching
      [docs/openapi.yaml](../docs/openapi.yaml), using
      `http://127.0.0.1:8001`.
- [ ] If creation succeeds, record the returned task ID.
- [ ] Verify `GET /tasks` at `http://127.0.0.1:8001/tasks`.
- [ ] Verify `GET /tasks/{id}` at the mapped host port.
- [ ] Verify `PUT /tasks/{id}` at the mapped host port.
- [ ] Verify `DELETE /tasks/{id}` at the mapped host port.
- [ ] Record actual response codes and bodies.
- [ ] Treat task-operation failures as possible evidence of the known
      TaskService integration defect.
- [ ] Do not claim CRUD validation unless these requests were actually run.

## Logs

- [ ] Review startup and runtime output:

      docker logs local-task-api

- [ ] Follow logs during smoke testing if needed:

      docker logs -f local-task-api

- [ ] Record actionable startup, database, or request errors.
- [ ] Distinguish application wiring errors from networking or database errors.

## SQLite persistence

- [ ] Confirm the application uses `/workspace/data/tasks.db`.
- [ ] Confirm the host bind mount or named volume is attached to
      `/workspace/data`.
- [ ] Confirm the mounted storage is writable.
- [ ] If task operations are available, stop and recreate the container, then
      verify expected data persistence.
- [ ] Do not use this SQLite setup as a high-concurrency or production
      deployment pattern.
- [ ] Back up any database file before destructive validation.
- [ ] Record that migrations, automated backups, replication, and
      multi-instance coordination are not provided.

## Shutdown and cleanup

- [ ] Stop the named container:

      docker stop local-task-api

- [ ] Remove it if it was not started with `--rm`:

      docker rm local-task-api

- [ ] Preserve or remove the host `data` directory deliberately.
- [ ] Do not delete a data directory containing records that must be retained.
- [ ] Remove temporary images or volumes only after confirming they are not
      needed.

## Security

- [ ] Keep local development bound to `127.0.0.1` where possible.
- [ ] Do not expose the unauthenticated API to an untrusted network.
- [ ] Restrict permissions on the host directory containing `tasks.db`.
- [ ] Do not commit secrets or place secrets in image layers, task payloads, or
      shell history.
- [ ] Treat SQLite files and container logs as potentially sensitive.
- [ ] Identify authentication, authorization, TLS, backups, and monitoring
      requirements before any production consideration.

## Known limitations

- [ ] Record that `app/main.py` currently uses a local stub `TaskService`
      instead of `app/services/task_service.py`.
- [ ] Record the independently verified baseline exactly: 11 tests collected,
      10 passed, 1 failed, and 1 warning.
- [ ] Record that `/workspace/data/tasks.db` is hard-coded.
- [ ] Record that pytest is not declared in `requirements.txt`.
- [ ] Record that there are no migrations, automated backups, replication,
      authentication, authorization, or multi-instance coordination.
- [ ] Record that the OpenAPI contract and some runtime error behavior are not
      fully aligned.
- [ ] Record separately whether Docker build, detached container startup,
      health checks at `http://127.0.0.1:8001`, and CRUD smoke tests were
      actually performed.
