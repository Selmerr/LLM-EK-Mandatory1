import sqlite3

def get_conn():
    conn = sqlite3.connect('notes.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # Configure to return rows as dictionaries
    return conn

def list_notes():
    conn = get_conn()
    cursor = conn.execute('SELECT id, title, content FROM notes')
    notes = [dict(row) for row in cursor.fetchall()]
    return notes

def create_note(title, content):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    new_id = cursor.lastrowid
    return {'id': new_id, 'title': title, 'content': content}

def delete_note(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (id,))
    if cursor.rowcount == 0:
        raise ValueError("Note with the specified ID does not exist.")
    conn.commit()
