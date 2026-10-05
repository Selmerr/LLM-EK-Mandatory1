You are implementation worker T001.

Read the architecture, OpenAPI contract, and task plan.

Implement only the storage layer.

Provide:
- list_notes()
- create_note(title, content)
- delete_note(id)

Use SQLite.

Only modify:
- mikkel-workflow/src/llm_man_1/storage.py

Do not create or modify tests.
Do not modify API files or documentation.

list_notes() must return note dictionaries containing id, title and content.

Ensure SQLite rows are converted correctly to dictionaries.

get_conn() must configure the SQLite connection with sqlite3.Row as its row_factory,
so list_notes() can return dictionaries containing id, title, and content.