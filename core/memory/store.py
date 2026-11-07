"""Small persistent SQLite conversation-memory store.

Store only information the application is authorized to retain. Avoid secrets
and sensitive personal data. This module does not infer or collect memories.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "memory" / "memory.sqlite3"


class MemoryStore:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path is not None else DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def add(self, content: str) -> int:
        content = content.strip()
        if not content:
            raise ValueError("Memory content must not be empty.")
        with self._connect() as connection:
            cursor = connection.execute("INSERT INTO memories(content) VALUES (?)", (content,))
            return int(cursor.lastrowid)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        terms = [term for term in query.split() if term]
        if not terms:
            return []
        where = " OR ".join("content LIKE ?" for _ in terms)
        params = [f"%{term}%" for term in terms] + [limit]
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT id, content, created_at FROM memories WHERE {where} ORDER BY id DESC LIMIT ?",
                params,
            ).fetchall()
        return [{"id": row[0], "content": row[1], "created_at": row[2]} for row in rows]

    def list_all(self, limit: int = 100) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, content, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [{"id": row[0], "content": row[1], "created_at": row[2]} for row in rows]
