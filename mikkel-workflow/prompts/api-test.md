You are the API testing worker.

Read:
- mikkel-workflow/src/llm_man_1/api.py
- mikkel-workflow/src/llm_man_1/storage.py
- mikkel-workflow/docs/openapi.yaml

Create:
- mikkel-workflow/tests/test_api.py

Test:
- GET /notes
- POST /notes
- DELETE /notes/{id}
- POST with missing required fields
- DELETE of a non-existent note

Use Flask's test client.
Only modify mikkel-workflow/tests/test_api.py.
Do not modify production code or documentation.
Keep the tests simple and compatible with pytest.
Flask error responses should be tested by checking the HTTP status code.
Do not expect Flask's test client to raise exceptions for normal 400/404 responses.

When POST /notes creates a note, capture the response and obtain the created ID
from that response before testing DELETE.
GET /notes may validly return an empty list.

For DELETE tests:
- Create a note using POST /notes inside the same test.
- Read its id from the POST response.
- Then DELETE that id.
- Do not use a note_id fixture.

For 400 and 404 cases, verify the HTTP status code only.
Do not assume the error response is JSON unless mikkel-workflow/docs/openapi.yaml explicitly requires it.

Output only the complete contents of the target file.
Do not output a filename.
Do not use Markdown fences.
Do not include explanations.