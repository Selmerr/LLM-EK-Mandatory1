You are the documentation worker.

Read:
- docs/architecture.md
- docs/openapi.yaml
- docs/tasks.md
- docs/quality.md
- Dockerfile
- artifacts/deployment.txt

Create:
- README.md

Write concise developer and operator documentation for the Notes API.

Include:

# Notes API

## Overview
Briefly describe the application and architecture.

## Requirements
List the main local requirements.

## Running Locally
Explain how to install dependencies and start the Flask application using uv.

## API Usage
Document:
- GET /notes
- POST /notes
- DELETE /notes/{id}

Include short curl examples.

## Testing
Explain how to run pytest.
Summarize the latest quality result from docs/quality.md without inventing results.

## Docker
Explain how to build and run the Docker image.

## Deployment Validation
Summarize the result from artifacts/deployment.txt.
Do not claim validation passed unless the log says it passed.

## Project Documentation
Reference:
- docs/architecture.md
- docs/openapi.yaml
- docs/tasks.md
- docs/quality.md

Only modify README.md.
Keep the documentation concise and factual.