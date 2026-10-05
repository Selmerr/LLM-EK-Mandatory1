You are the storage testing worker.

Read:
- src/llm_man_1/storage.py
- docs/tasks.md

Create:
- tests/test_storage.py

Rules:
- Import storage functions from llm_man_1.storage.
- Do not assume return values that the implementation does not provide.
- Do not create a fake database fixture unless the production code can actually use it.
- Create test data explicitly when needed.
- Verify delete_note() by checking that the note is gone afterwards.
- Keep tests compatible with pytest.

Only modify tests/test_storage.py.
Do not modify production code or documentation.