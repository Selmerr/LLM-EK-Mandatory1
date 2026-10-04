You are implementation worker T002.

Read the architecture, OpenAPI contract, and task plan.

Implement only the Flask API layer.

Implement:
- GET /notes
- POST /notes
- DELETE /notes/{id}

Assume these storage functions exist:
- list_notes()
- create_note(title, content)
- delete_note(id)

Write API tests.

Only modify:
- src/llm_man_1/api.py
- tests/test_api.py

Do not modify storage files or documentation.