import pytest
from mikkel_workflow.src.llm_man_1.storage import (
    get_conn,
    list_notes,
    create_note,
    delete_note,
)
from pathlib import Path

@pytest.fixture(scope="module")
def tmp_db_path():
    """Create a temporary SQLite database file path for testing."""
    temp_dir = Path(__file__).parent / "tmp"
    temp_dir.mkdir(exist_ok=True)
    db_file = temp_dir / f"notes_{Path.cwd().name}_{Path.cwd().resolve()}.db"
    return str(db_file)

@pytest.fixture(scope="module")
def monkeypatch_get_conn(tmp_db_path):
    """Monkeypatch get_conn to use the temporary database file."""
    def patched_get_conn():
        conn = sqlite3.connect(str(tmp_db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    yield patched_get_conn  # replace original get_conn with this function

def test_list_notes(monkeypatch_get_conn):
    """Test that list_notes returns all notes created in the session."""
    notes = list_notes()
    assert len(notes) == 0, "Expected no notes initially"

def test_create_note(monkeypatch_get_conn):
    title = "Test Title"
    content = "This is a test note."
    new_note = create_note(title, content)
    assert new_note['id'] != 0, "ID should not be zero for newly created note"
    assert list_notes()[0]['title'] == title, "Listed note must match the one we created"

def test_delete_note(monkeypatch_get_conn):
    # Create a note to delete
    create_note("Delete Me", "Temporary content")
    
    # Delete the note by its ID returned from create_note()
    note_id = list_notes()[0]['id']
    assert delete_note(note_id) is None, f"Note with id {note_id} should be deleted"
    
    # Verify deletion
    assert list_notes() == [], "List of notes should be empty after deleting the only note"

# End of file
