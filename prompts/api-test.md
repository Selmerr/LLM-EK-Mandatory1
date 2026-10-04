You are the API testing worker.

Read:
- src/llm_man_1/api.py
- src/llm_man_1/storage.py
- docs/openapi.yaml

Create:
- tests/test_api.py

Test:
- GET /notes
- POST /notes
- DELETE /notes/{id}
- POST with missing required fields
- DELETE of a non-existent note

Use Flask's test client.
Only modify tests/test_api.py.
Do not modify production code or documentation.
Keep the tests simple and compatible with pytest.
Flask error responses should be tested by checking the HTTP status code.
Do not expect Flask's test client to raise exceptions for normal 400/404 responses.

When POST /notes creates a note, capture the response and obtain the created ID
from that response before testing DELETE.