# Architecture Overview

## Component Decomposition & Responsibilities
- **Flask App**: Handles HTTP requests, routes them to the appropriate note handler, and returns JSON responses.
- **Note Handler**: Manages CRUD operations for notes (GET/POST/DELETE /notes).
- **Storage Layer**: Interfaces with SQLite or in-memory storage for persisting notes.

## Deployment Topology & Constraints
The application runs as a single Docker container. It exposes port 5000 for the Flask app and relies on environment variables for configuration such as database connection strings. The container must be stateless to allow horizontal scaling.

## ADR: In-Memory vs SQLite Storage

**Context**: We need a storage solution that balances performance, simplicity, and persistence requirements for our notes API.

**Options Considered**:
1. **In-Memory Storage (e.g., Python dict)** - Fast access but loses data on container restart.
2. **SQLite Database** - Persistent, supports transactions, and integrates easily with Flask-SQLAlchemy.

**Decision**: Choose SQLite as the storage backend.

**Consequences**:
- **Positive**: Data persistence across container restarts, easier debugging with SQL tools, and compatibility with standard relational operations.
- **Negative**: Slight overhead for database connections and migrations compared to in-memory solutions. Requires managing a persistent volume or using Docker volumes for data longevity.
