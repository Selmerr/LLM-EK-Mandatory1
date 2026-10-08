---
title: Task API Architecture
---

## Component Responsibilities

- **Client**: Sends HTTP requests to the API
- **FastAPI**: Handles routing and request/response processing
- **Service Layer**: Contains business logic for task operations
- **SQLite Repository**: Manages database interactions
- **SQLite Database**: Stores task data persistently

## Data Flow

Client → FastAPI API → Service Layer → SQLite Repository → SQLite Database

## Deployment Topology

- Single-node architecture
- No external dependencies
- Persistent SQLite database file (`data/tasks.db`)

## Constraints

- No authentication
- No external APIs
- Limited to local execution
- SQLite for simplicity and portability