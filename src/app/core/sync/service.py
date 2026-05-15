from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List

from ..database.db import Database
from ..models import PlaylistItem
from ..scanner.playlist_scanner import PlaylistScanner
from ..sync.diff_engine import DiffEngine
from ..sync.filesystem import list_files
from ..utils.naming import make_filename, sanitize_title
from ..utils.yt import extract_playlist_id


class SyncService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.scanner = PlaylistScanner()
        self.diff = DiffEngine()

    def _mode_to_extension(self, mode: str) -> str:
        if mode == "audio":
            return ".mp3"
        if mode == "video":
            return ".mp4"
        return ".mp3"  # default for MVP

    def sync_from_config(self, playlist_cfg: dict) -> List[dict]:
        url: str = playlist_cfg.get("url")
        mode: str = playlist_cfg.get("download_mode", "audio")
        save_path = Path(playlist_cfg.get("save_path", "./downloads")).resolve()
        save_path.mkdir(parents=True, exist_ok=True)

        playlist_id = extract_playlist_id(url) or url
        ext = self._mode_to_extension(mode)

        items = self.scanner.scan(url, playlist_id)

        sanitized: List[PlaylistItem] = []
        for it in items:
            safe_title = sanitize_title(it.title, it.video_id)
            sanitized.append(
                PlaylistItem(
                    playlist_id=it.playlist_id,
                    video_id=it.video_id,
                    title=safe_title,
                    playlist_index=it.playlist_index,
                    local_filename=None,
                    downloaded=False,
                )
            )

        rows = [
            (
                it.playlist_id,
                it.video_id,
                it.title,
                it.playlist_index,
                None,
                0,
            )
            for it in sanitized
        ]
        self.db.upsert_playlist_items(rows)

        db_index_rows = self.db.get_items_index(playlist_id)
        db_index: dict[str, PlaylistItem] = {}
        for vid, row in db_index_rows.items():
            db_index[vid] = PlaylistItem(
                playlist_id=row["playlist_id"],
                video_id=row["video_id"],
                title=row["title"],
                playlist_index=row["playlist_index"],
                local_filename=row["local_filename"],
                downloaded=bool(row["downloaded"]),
            )

        mode_dir = "audio" if ext == ".mp3" else "video"
        fs_root = (save_path / mode_dir)
        fs_entries = list_files(fs_root, [ext])

        actions = self.diff.compute_actions(sanitized, db_index, fs_entries, ext)

        return [
            {
                "type": a.type,
                "video_id": a.item.video_id if a.item else None,
                "from_name": a.from_name,
                "to_name": a.to_name,
            }
            for a in actions
        ]
