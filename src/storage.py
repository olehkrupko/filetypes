import sqlite3
import typing
from .scanner import FileInfo


class Storage:
    def __init__(self, db_path: str = "cache/files.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    extension TEXT,
                    size_bytes INTEGER,
                    last_modified REAL
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)")
            conn.commit()

    def clear_cache(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM files")
            conn.commit()

    def upsert_files(self, files: typing.Iterable[FileInfo], batch_size: int = 10000):
        """Batch insert files to improve performance"""
        with sqlite3.connect(self.db_path) as conn:
            batch = []
            for file in files:
                batch.append(
                    (file.path, file.extension, file.size_bytes, file.last_modified)
                )
                if len(batch) >= batch_size:
                    conn.executemany(
                        "INSERT OR REPLACE INTO files "
                        "(path, extension, size_bytes, last_modified) VALUES (?, ?, ?, ?)",
                        batch,
                    )
                    batch = []

            if batch:
                conn.executemany(
                    "INSERT OR REPLACE INTO files "
                    "(path, extension, size_bytes, last_modified) VALUES (?, ?, ?, ?)",
                    batch,
                )
            conn.commit()

    def get_stats(self) -> typing.List[typing.Tuple[str, int, int]]:
        """Returns list of (extension, count, total_size_bytes)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT extension, COUNT(*), SUM(size_bytes)
                FROM files
                GROUP BY extension
                ORDER BY COUNT(*) DESC
            """
            )
            return cursor.fetchall()

    def get_files_by_extension(self, extension: str) -> typing.List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT path FROM files WHERE extension = ? ORDER BY path", (extension,)
            )
            return [row[0] for row in cursor.fetchall()]
