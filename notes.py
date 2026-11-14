import sqlite3
from contextlib import closing
from pathlib import Path


class Notes:
    def __init__(self, path: Path):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection, connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def list_all(self) -> list[sqlite3.Row]:
        with closing(self.connect()) as connection:
            return connection.execute(
                "SELECT id, title, created_at FROM notes ORDER BY id DESC"
            ).fetchall()

    def get(self, note_id: int) -> sqlite3.Row | None:
        with closing(self.connect()) as connection:
            return connection.execute(
                "SELECT * FROM notes WHERE id = ?", (note_id,)
            ).fetchone()

    def create(self, title: str, body: str) -> int:
        with closing(self.connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO notes (title, body) VALUES (?, ?)", (title, body)
            )
            return cursor.lastrowid
