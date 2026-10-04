Project: a small notes REST API in Python (Flask), run as a single Docker container.
Write docs/architecture.md in plain markdown. Do not include YAML or code blocks.
Sections: component decomposition and responsibilities; deployment topology and
constraints; one ADR choosing between in-memory and SQLite storage (context,
options, decision, consequences).
The API contract lives in a separate file, docs/openapi.yaml. Refer to it by name only.
Keep it under 80 lines.