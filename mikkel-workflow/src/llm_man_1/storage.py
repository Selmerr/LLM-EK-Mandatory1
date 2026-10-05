import sqlite3

DB_NAME = 'notes.db'

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create table if it doesn't exist (run once on startup)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    # Configure row_factory to sqlite3.Row for dictionary access
    conn.row_factory = sqlite3.Row
    return conn

def list_notes():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes")
    rows = cursor.fetchall()
    # Convert sqlite3.Row objects to dicts containing id, title, and content
    notes = [dict(row) for row in rows]
    conn.close()
    return notes

def create_note(title, content):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": new_id}

def delete_note(note_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
    rows_affected = cursor.rowcount
    if rows_affected == 0:
        raise ValueError(f"No note found with ID {note_id}")
    conn.commit()
    conn.close()
