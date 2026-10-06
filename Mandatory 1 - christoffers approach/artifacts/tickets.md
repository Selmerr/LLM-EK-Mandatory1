### Tickets

Here are the incremental development tickets based on the provided requirements:

1. **TKT-001**: Initialize SQLite database file and schema  
   *Description*: Create the database file at `/app/data/books.db` and define the table schema with columns: `id` (integer, primary key, autoincrement), `title` (text, not null), `author` (text, not null), `year` (integer, not null), `isbn` (text).  
   *Acceptance Criteria*:  
   - File exists at `/app/data/books.db`  
   - Table `books` has the specified schema with all required constraints  

2. **TKT-002**: Implement POST `/books` endpoint with validation and insertion  
   *Description*: Handle HTTP POST requests to `/books` with validation of `title` (min 3 chars), `author` (min 2 chars), `year` (integer ≥ 1800), then insert into the database. Return 201 Created with the book object (`id`, `title`, `author`, `year`).  
   *Acceptance Criteria*:  
   - Request body must contain `title`, `author`, `year`  
   - Validation fails with appropriate 4xx errors (e.g., `title` too short → 400 Bad Request)  
   - Book is inserted into the database and returned with generated `id`  

3. **TKT-003**: Implement GET `/books` endpoint with pagination  
   *Description*: Handle HTTP GET requests to `/books` with optional query parameters `page` (default: 1) and `limit` (default: 10). Return paginated list of books (`id`, `title`, `author`, `year`).  
   *Acceptance Criteria*:  
   - Returns 200 OK with paginated results (e.g., `books: [ {...}, {...} ]`)  
   - Handles invalid `page`/`limit` values (e.g., negative integers → 400)  
   - Uses database pagination (e.g., `LIMIT`/`OFFSET` in SQL)  

4. **TKT-004**: Implement GET `/books/{id}` endpoint with resource retrieval  
   *Description*: Handle HTTP GET requests to `/books/{id}` to return a single book (`id`, `title`, `author`, `year`) if exists, or 404 Not Found otherwise.  
   *Acceptance Criteria*:  
   - Returns 200 OK with book data if `id` exists  
   - Returns 404 Not Found if `id` does not exist in the database  

5. **TKT-005**: Implement PUT `/books/{id}` endpoint with update validation  
   *Description*: Handle HTTP PUT requests to `/books/{id}` with validation of `title` (min 3 chars), `author` (min 2 chars), `year` (integer ≥ 1800), then update the book. Return 200 OK with updated book or 404 Not Found.  
   *Acceptance Criteria*:  
   - Updates the book record for the given `id`  
   - Validation fails with appropriate 4xx errors (e.g., `year` invalid → 400)  
   - Returns updated book object (`id`, `title`, `author`, `year`)  

6. **TKT-006**: Implement DELETE `/books/{id}` endpoint with no-body response  
   *Description*: Handle HTTP DELETE requests to `/books/{id}` to remove a book and return 204 No Content (no body).  
   *Acceptance Criteria*:  
   - Book is deleted from the database  
   - Returns 204 No Content (no response body)  

7. **TKT-007**: Implement global error handling for structured JSON responses  
   *Description*: Ensure all endpoints return structured JSON responses with HTTP status codes (e.g., 400, 404, 200) in case of errors.  
   *Acceptance Criteria*:  
   - All error cases return JSON with a `message` key (e.g., `{ "message": "Invalid year" }`)  
   - No HTTP 204 responses with body (per standard)  
   - Consistent error handling across all endpoints  

---

### Architecture Issues

The following contradictions were identified in the requirements that must be resolved before implementation:

1. **HTTP 204 No Content vs. JSON Body Contradiction**  
   *Issue*: The requirements specify that the DELETE endpoint (`/books/{id}`) returns a JSON body (`{ "message": "Book deleted" }`) with HTTP status `204 No Content`. This violates the HTTP standard, which states that **204 No Content must have no body**.  
   *Impact*: This would cause clients to fail parsing the response (since 204 bodies are forbidden).  
   *Resolution Required*: Either:  
   - Remove the JSON body requirement and use pure 204 No Content (no body), **or**  
   - Change the status code to `200 OK` with the JSON body (e.g., `{"message": "Book deleted"}`).  

2. **ISBN Length Constraint Not Enforced in Schema**  
   *Issue*: The requirements define `isbn` as a string with a maximum length of 13 characters, but the SQLite schema uses `TEXT` (which does not enforce length constraints).  
   *Impact*: The database could store invalid ISBNs (e.g., 20-character strings).  
   *Resolution Required*: Update the SQLite schema to enforce `isbn` length (e.g., `isbn TEXT CHECK (LENGTH(isbn) <= 13)`).  

> These issues are critical for correct implementation. TKT-006 and TKT-001 must be adjusted to reflect the resolved contradictions. The initial tickets assume the 204 No Content with no body (standard practice) and the ISBN length constraint is enforced via schema.