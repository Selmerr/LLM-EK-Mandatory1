You are the technical lead.

Read:
- docs/architecture.md
- docs/openapi.yaml

Create docs/tasks.md.

Only plan functionality defined in docs/openapi.yaml.
Do not invent additional endpoints or requirements.

Create at least two implementation tasks.

Each task must include:
- task ID
- scope boundaries
- dependencies
- acceptance criteria

Partition the work so that at least two implementation workers can work
independently.

Suggested split:
- storage/persistence
- Flask API/routes

Do not implement anything.
Do not modify architecture or API files.
Do not plan operations that are not defined in docs/openapi.yaml.

The two implementation tasks must not depend on each other.
They must be suitable for parallel execution.

Do not invent authentication or other requirements not present in the architecture or API contract.
Keep the document concise.