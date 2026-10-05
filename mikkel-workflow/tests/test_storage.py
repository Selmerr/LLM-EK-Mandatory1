import pytest
from llm_man_1.storage import get_conn, list_notes, create_note, delete_note

@pytest.fixture(scope='module')
def db_path():
    import tempfile
    temp_dir = tempfile.TemporaryDirectory().name
    return f"{temp_dir}/notes.db"

@pytest.mark.usefixtures("db_path")
class TestStorage:
    def test_list_notes_empty(self, db_path):
        # Ensure list_notes returns empty list for a fresh DB
        conn = get_conn(db_path)
        assert list(list_notes(conn)) == []

    def test_create_note(self, db_path):
        # Create a new note and verify it's in the list
        title = "Test Note"
        content = "This is a test."
        conn = get_conn(db_path)
        note_id = create_note(title, content, conn).get("id")
        assert note_id is not None

        notes = list(list_notes(conn))
        assert len(notes) == 1
        assert notes[0]["title"] == title

    def test_delete_note(self, db_path):
        # Create a note and then delete it, verifying deletion
        title = "Delete Me"
        content = "Temporary note for deletion testing."
        conn = get_conn(db_path)
        note_id = create_note(title, content, conn).get("id")
        assert note_id is not None

        # Attempt to delete the note
        delete_note(note_id, conn)

        # Verify the note no longer exists
        notes = list(list_notes(conn))
        assert len(notes) == 0
