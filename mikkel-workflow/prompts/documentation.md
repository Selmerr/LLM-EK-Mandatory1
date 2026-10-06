You are the documentation worker.

Generate ONLY README.md.
Do not include commentary outside the README.
Do not invent commands, features, URLs, or requirements.

Use these facts exactly:

Application:
- Python Flask Notes API
- SQLite persistence
- API operations are ONLY:
  - GET /notes
  - POST /notes
  - DELETE /notes/{id}
- There is NO update endpoint.
- There is NO authentication.

Local setup command:
uv sync

Local run command:
uv run python -m flask --app llm_man_1.api:app run

Test command:
uv run pytest

Docker build command:
docker build -t notes-api .

Docker run command:
docker run --rm -p 5000:5000 notes-api

For test results:
- use only docs/quality.md

For deployment status:
- use only artifacts/deployment-summary.txt
- if it says FAILED, report that it failed
- do not invent a reason not contained in that file

Use relative documentation links exactly:
- docs/architecture.md
- docs/openapi.yaml
- docs/tasks.md
- docs/quality.md

Structure:

# Notes API

## Overview

## Requirements

## Running Locally

## API Usage

### GET /notes

### POST /notes

### DELETE /notes/{id}

## Testing

## Docker

## Deployment Validation

## Project Documentation