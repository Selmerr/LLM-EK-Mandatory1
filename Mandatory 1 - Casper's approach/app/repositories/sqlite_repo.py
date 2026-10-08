import sqlite3
import os
from typing import Dict, List, Optional


class SQLiteRepo:
    def __init__(self):
        os.makedirs('/workspace/data', exist_ok=True)
        self.conn = sqlite3.connect('/workspace/data/tasks.db', check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority INTEGER,
                due_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create(self, task_data: Dict) -> None:
        self.conn.execute('''
            INSERT INTO tasks (id, title, description, status, priority, due_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data["id"], task_data["title"], task_data["description"],
            task_data["status"], task_data["priority"], task_data["due_date"],
            task_data["created_at"], task_data["updated_at"]
        ))
        self.conn.commit()

    def get(self, task_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "due_date": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            }
        return None

    def list(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "due_date": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            }
            for row in rows
        ]

    def update(self, task_id: str, task_data: Dict) -> None:
        self.conn.execute('''
            UPDATE tasks
            SET title = ?, description = ?, status = ?, priority = ?, due_date = ?, updated_at = ?
            WHERE id = ?
        ''', (
            task_data["title"], task_data["description"], task_data["status"],
            task_data["priority"], task_data["due_date"], task_data["updated_at"], task_id
        ))
        self.conn.commit()

    def delete(self, task_id: str) -> None:
        self.conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()