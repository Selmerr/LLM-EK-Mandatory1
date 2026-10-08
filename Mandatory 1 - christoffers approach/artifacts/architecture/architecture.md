## REST API Architecture for Book Management

### 1. System Overview
A minimal, production-ready REST API service enabling CRUD operations for book entities via HTTP. Uses a single backend service with SQLite as the primary data store for simplicity and rapid development.

### 2. Component Decomposition
| Component          | Description                                  |
|---------------------|----------------------------------------------|
| Book API Service    | Handles all REST requests and business logic  |
| SQLite Database     | Stores book data (in-memory for dev, file-based for production) |

### 3. Responsibilities of Each Component
- **Book API Service**:  
  - Validates and processes HTTP requests  
  - Maps requests to database operations  
  - Returns structured JSON responses with HTTP status codes  
  - Enforces data constraints (e.g., non-empty titles)  
- **SQLite Database**:  
  - Stores book records in a single `books` table  
  - Manages data persistence and transactions  
  - Handles schema migrations via database migrations tool (e.g., `sqlite3` CLI)  

### 4. Interface/API Contracts
| HTTP Method | Endpoint      | Request Body (JSON)                           | Response (JSON)                          | Status Code |
|-------------|----------------|------------------------------------------------|-------------------------------------------|--------------|
| POST        | `/books`       | `{ "title": "string", "author": "string", "year": 1900 }` | `{ "id": 1, "title": "...", ... }` | 201 Created |
| GET         | `/books`       | `{}` (optional query: `?page=1&limit=10`)       | `[ { "id": 1, ... }, ... ]`             | 200 OK       |
| GET         | `/books/{id}` | `{}`                                           | `{ "id": 1, ... }`                      | 200 OK       |
| PUT         | `/books/{id}` | `{ "title": "string", ... }`                   | `{ "id": 1, ... }`                      | 200 OK       |
| DELETE      | `/books/{id}` | `{}`                                           | `{ "message": "Book deleted" }`         | 204 No Content |

*Note: All IDs are integers. `year` is required (integer ≥ 1800). `title` and `author` are required strings.*

### 5. Data Model
```json
{
  "id": 1,
  "title": "string (min 3 chars)",
  "author": "string (min 2 chars)",
  "year": 1900,
  "isbn": "string (optional, max 13 chars)"
}
```
*SQLite Table Schema:*  
`books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT NOT NULL, year INTEGER NOT NULL, isbn TEXT)`

### 6. Deployment Topology
- **Single Docker container** for the Book API Service (ports: `8080`)
- **SQLite database file** stored in container's `/app/data/books.db` (volume mounted for persistence)
- **No external dependencies** (e.g., no cloud services, no message queues)
- **Development**: Run via `docker-compose up` (separate `db` service for production)
- **Production**: Deploy as single container with environment variables for DB path

### 7. Important Technical Constraints
1. **No authentication required** (simple CRUD demo; add JWT/basic auth if needed later)
2. **SQLite only** (file-based storage for simplicity; not suitable for production scale)
3. **HTTP 204 responses** for DELETE (no body)
4. **All IDs are integers** (no UUIDs)
5. **Strict input validation** (e.g., `year` must be integer ≥ 1800)

### 8. Architecture Decisions
1. **Single-service design** instead of microservices: Avoids complexity for a simple CRUD API (aligns with "simple" requirement).
2. **SQLite as default DB**: Eliminates database configuration overhead; sufficient for development/testing.
3. **No API versioning**: Keeps contracts simple for initial release (add versioning later if needed).
4. **JSON responses with minimal fields**: Ensures predictable client interactions without over-fetching.
5. **In-memory validation**: Business rules (e.g., title length) enforced at API layer, not DB (flexible for future changes).

---

This architecture delivers a production-ready, minimal book management API in <10 minutes to implement. All components are explicitly defined, with clear boundaries and constraints to prevent over-engineering.