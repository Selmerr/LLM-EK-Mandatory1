# README.md

## Overview

This is a simple Notes API developed using Python Flask and SQLite for persistence. The API supports CRUD operations on notes, with GET, POST, and DELETE methods available at `/notes`, `/notes/{id}`, respectively.

## Requirements

- Python 3.x
- Flask (included in the Docker image)
- SQLite database library (`sqlite3`)

## Running Locally

To run the application locally:

```bash
uv run flask --app llm_man_1.api:app run
```

This command starts a development server on port 5000. You can access the API at `http://localhost:5000`.

### Testing

Run tests using:

```bash
uv run pytest
```

## API Usage

### GET /notes

Retrieve a list of all notes.

### POST /notes

Create a new note with title and content.

### DELETE /notes/{id}

Delete a specific note identified by `{id}`.

## Docker

To build the Docker image:

```bash
docker build -t notes-api .
```

Then run the container:

```bash
docker run --rm -p 5000:5000 notes-api
```

This will expose port 5000 and map it to your local machine, allowing you to access the API via `http://localhost:5000`.

## Deployment Validation

The deployment status is as follows:

- **Deployment Status**: PASSED (based on artifacts/deployment-summary.txt)

## Project Documentation

For more detailed information about architecture, openAPI specification, and tasks involved in development, refer to the following documents:
- [Architecture Overview](docs/architecture.md)
- [OpenAPI Specification](docs/openapi.yaml)
- [Task List for Notes API Development](docs/tasks.md)
