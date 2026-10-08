You are the storage testing worker.

Read:
- mikkel-workflow/src/llm_man_1/storage.py
- mikkel-workflow/docs/tasks.md

Create:
- mikkel-workflow/tests/test_storage.py

Rules:
- Import storage functions from llm_man_1.storage.
- Do not assume return values that the implementation does not provide.
- Do not create a fake database fixture unless the production code can actually use it.
- Create test data explicitly when needed.
- Verify delete_note() by checking that the note is gone afterwards.
- Keep tests compatible with pytest.

Only modify mikkel-workflow/tests/test_storage.py.
Do not modify production code or documentation.

Use pytest's monkeypatch and tmp_path to temporarily replace
llm_man_1.storage.DB_NAME with a temporary database path.

Do not create a separate SQLite connection that the production functions do not use.

When testing deletion, use the ID returned by create_note().
Do not hard-code IDs.

Output only the complete contents of the target file.
Do not output a filename.
Do not use Markdown fences.
Do not include explanations.