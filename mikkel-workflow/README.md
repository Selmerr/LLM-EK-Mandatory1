# README.md

## Overview
This is a Notes API built using Python Flask and SQLite for persistence. The API supports the following operations:
- **GET /notes**: Retrieve all notes.
- **POST /notes**: Create a new note.
- **DELETE /notes/{id}**: Delete a specific note identified by its ID.

No update endpoint or authentication functionality is provided.

## Requirements
- Python 3.12 or later
- SQLite database

## Running Locally
To run the application locally, execute:
```bash
uv run flask --app llm_man_1.api:app run
```

## API Usage
### GET /notes
Retrieve a list of all notes.

### POST /notes
Create a new note. The request body should be in JSON format with `title` and `content` fields.

### DELETE /notes/{id}
Delete a specific note identified by the provided ID.

## Testing
To run tests, execute:
```bash
uv run pytest
```

## Docker
To build and run the application using Docker, use these commands:
```bash
docker build -t notes-api .
docker run --rm -p 5000:5000 notes-api
```

## Deployment Validation
The deployment status can be checked in `artifacts/deployment-summary.txt`. The current status is FAILED as indicated by the file contents.

## Project Documentation
For more detailed information, refer to:
- Architecture overview: [docs/architecture.md](docs/architecture.md)
- API specification: [docs/openapi.yaml](docs/openapi.yaml)
- Task list for development: [docs/tasks.md](docs/tasks.md)
