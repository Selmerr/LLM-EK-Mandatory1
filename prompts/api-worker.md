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

Do not modify storage files or documentation.