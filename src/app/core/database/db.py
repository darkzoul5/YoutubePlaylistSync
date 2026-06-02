from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS playlists (
    id TEXT PRIMARY KEY,
    name TEXT,
    url TEXT,
    path TEXT,
    mode TEXT,
    auto_sync INTEGER,
    sync_interval_minutes INTEGER,
    last_sync TEXT
);

CREATE TABLE IF NOT EXISTS playlist_items (
    playlist_id TEXT,
    video_id TEXT,
    title TEXT,
    playlist_index INTEGER,
    local_filename TEXT,
    downloaded INTEGER,
    last_seen TEXT,
    PRIMARY KEY (playlist_id, video_id)
);
"""


class Database:
    """Thin SQLite persistence layer for playlists and playlist items.

    The database stores the local synchronization state so the sync pipeline
    can compare remote playlist data with what has already been downloaded,
    renamed, or marked as removed.
    """

    def __init__(self, db_path: Path) -> None:
        self.path = db_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        """Create the schema if this database has not been initialized yet."""
        with self._conn:
            self._conn.executescript(SCHEMA)

    def upsert_playlist_items(self, rows: Iterable[tuple]):
        """Insert or refresh the cached metadata for playlist entries."""
        sql = (
            "INSERT INTO playlist_items (playlist_id, video_id, title, playlist_index, local_filename, downloaded, last_seen) "
            "VALUES (?, ?, ?, ?, ?, ?, datetime('now')) "
            "ON CONFLICT(playlist_id, video_id) DO UPDATE SET "
            "title=excluded.title, playlist_index=excluded.playlist_index, local_filename=excluded.local_filename, "
            "downloaded=excluded.downloaded, last_seen=datetime('now')"
        )
        with self._conn:
            self._conn.executemany(sql, rows)

    def get_items_index(self, playlist_id: str) -> dict[str, sqlite3.Row]:
        """Return all cached items for a playlist keyed by video id."""
        cur = self._conn.execute(
            "SELECT * FROM playlist_items WHERE playlist_id = ?",
            (playlist_id,),
        )
        return {row["video_id"]: row for row in cur.fetchall()}

    def upsert_playlist(self, *, id: str, name: str | None, url: str, path: str, mode: str, auto_sync: int = 0, sync_interval_minutes: int = 0) -> None:
        """Insert or update the playlist configuration row."""
        sql = (
            "INSERT INTO playlists (id, name, url, path, mode, auto_sync, sync_interval_minutes, last_sync) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, NULL) "
            "ON CONFLICT(id) DO UPDATE SET name=excluded.name, url=excluded.url, path=excluded.path, mode=excluded.mode, "
            "auto_sync=excluded.auto_sync, sync_interval_minutes=excluded.sync_interval_minutes"
        )
        with self._conn:
            self._conn.execute(sql, (id, name, url, path, mode, auto_sync, sync_interval_minutes))

    def update_local_filename(self, playlist_id: str, video_id: str, local_filename: str | None) -> None:
        """Record the current filename associated with a playlist item."""
        with self._conn:
            self._conn.execute(
                "UPDATE playlist_items SET local_filename = ?, last_seen = datetime('now') WHERE playlist_id = ? AND video_id = ?",
                (local_filename, playlist_id, video_id),
            )

    def mark_downloaded(self, playlist_id: str, video_id: str, downloaded: bool) -> None:
        """Mark whether a playlist item is present on disk."""
        with self._conn:
            self._conn.execute(
                "UPDATE playlist_items SET downloaded = ?, last_seen = datetime('now') WHERE playlist_id = ? AND video_id = ?",
                (1 if downloaded else 0, playlist_id, video_id),
            )

    def clear_file_state(self, playlist_id: str, video_id: str) -> None:
        """Clear filename and downloaded flags after a deletion or recycle."""
        with self._conn:
            self._conn.execute(
                "UPDATE playlist_items SET local_filename = NULL, downloaded = 0, last_seen = datetime('now') WHERE playlist_id = ? AND video_id = ?",
                (playlist_id, video_id),
            )

    def set_playlist_last_sync(self, playlist_id: str) -> None:
        """Store the timestamp of the most recent successful sync."""
        with self._conn:
            self._conn.execute(
                "UPDATE playlists SET last_sync = datetime('now') WHERE id = ?",
                (playlist_id,),
            )

    def get_playlist_last_sync(self, playlist_id: str) -> str | None:
        """Return the last sync timestamp for a playlist, if any."""
        cur = self._conn.execute("SELECT last_sync FROM playlists WHERE id = ?", (playlist_id,))
        row = cur.fetchone()
        if not row:
            return None
        return row["last_sync"]
