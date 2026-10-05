You are implementation worker T002.

Implement only the Flask API layer.

Implement:
- GET /notes
- POST /notes
- DELETE /notes/{id}

The storage interface is provided by mikkel-workflow/src/llm_man_1/storage.py.

Import these functions from llm_man_1.storage:
- list_notes
- create_note
- delete_note

Do NOT define or stub these functions yourself.

Only modify:
- mikkel-workflow/src/llm_man_1/api.py

Do not modify storage files, tests, or documentation.