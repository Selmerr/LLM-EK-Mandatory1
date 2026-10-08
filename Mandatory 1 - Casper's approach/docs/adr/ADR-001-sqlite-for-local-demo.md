---
title: ADR-001-sqlite-for-local-demo
---

## Context

The project is a local FastAPI task demo used in an Open WebUI multi-LLM
coding workflow evaluation. It needs persistence for local task operations
without requiring a separately managed database server.

The current repository implementation uses `SQLiteRepo` and stores the database
at `/workspace/data/tasks.db`. The intended application flow is FastAPI routes
to `TaskService`, then to `SQLiteRepo` and SQLite.

The current application wiring has a known defect: `app/main.py` uses a local
stub `TaskService` instead of the real service implementation. This ADR records
the database decision and does not resolve that application defect.

## Decision

Use SQLite for this local evaluation/demo.

The existing repository implementation uses the database path
`/workspace/data/tasks.db`. For container execution, provide that directory as
writable storage and mount it from the host or a named volume when persistence
across container replacement is required.

SQLite is explicitly not being selected as a general production database
strategy and must not be treated as appropriate for high-concurrency workloads.

## Alternatives considered

### PostgreSQL

PostgreSQL would provide a stronger foundation for concurrent access,
multi-instance deployment, operational controls, and production workloads. It
was not selected because it introduces a separate service and configuration
burden outside the scope of this local demo.

### MySQL

MySQL would also provide a client/server database suitable for broader
deployment scenarios. It was not selected because the local evaluation does not
require a separate database service.

### In-memory storage

In-memory storage would minimize setup but would lose data whenever the process
restarts. It does not meet the demo's need to exercise file-backed persistence.

## Rationale

SQLite best matches the local-demo constraint: it provides durable,
file-backed storage while avoiding external infrastructure. The simplicity is
valuable for repeatable local evaluation, provided the scope remains a
single-node, low-volume workflow.

## Consequences

### Positive

- No separate database server is required.
- Local setup and teardown are simple.
- The database is inspectable and portable as a file.
- The deployment topology remains small and suitable for evaluation.

### Negative

- Persistence depends on a writable filesystem at the hard-coded path.
- Container data is lost when the container is removed unless storage is
  mounted externally.
- Concurrent writers and multiple application instances are outside the target
  operating model.
- The repository provides no automated migrations, backup, replication, or
  recovery process.
- The database file requires filesystem permission controls.
- The current TaskService integration defect prevents the intended SQLite-backed
  path from being exercised consistently.

## Limitations

- SQLite is not appropriate for high-concurrency or production workloads in this
  project.
- There is no authentication, authorization, encryption-at-rest policy,
  backup automation, replication, or multi-instance coordination.
- The hard-coded `/workspace/data/tasks.db` path reduces portability outside
  environments that can provide that directory.
- The current `TaskService` integration defect in `app/main.py` must be fixed in
  application code before the intended SQLite-backed task workflow can operate.
- This decision does not establish that Docker deployment or API CRUD has been
  validated.
