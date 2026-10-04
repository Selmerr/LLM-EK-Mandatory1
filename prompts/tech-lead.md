You are the technical lead.

Read:
- docs/architecture.md
- docs/openapi.yaml

Create docs/tasks.md.

Only plan functionality defined in docs/openapi.yaml.
Do not invent additional endpoints or requirements.

Create at least two implementation tasks that can be worked on independently
by separate coding workers.

Each task must include:
- task ID
- scope
- files affected
- dependencies
- acceptance criteria

Partition the work so workers modify different files.

Suggested split:
- one task for storage/persistence
- one task for Flask API/routes

Both tasks may depend on the architecture and API contract, but must not
depend on each other.

Do not implement anything.
Do not modify architecture or API files.
Keep the document concise.