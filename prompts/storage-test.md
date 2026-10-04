You are the storage testing worker.

Read:
- src/llm_man_1/storage.py
- docs/tasks.md

Create:
- tests/test_storage.py

Test:
- list_notes()
- create_note(title, content)
- delete_note(id)
- deletion of a non-existent note

Only modify tests/test_storage.py.
Do not modify production code or documentation.
Keep the tests simple and compatible with pytest.
Do not assume the database already contains data.
Create the data needed by each test.

Do not assume return values that are not defined by the implementation or contract.
Verify deletion by checking the resulting stored data.

Use an isolated temporary database where possible.