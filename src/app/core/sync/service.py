from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Mapping, Sequence

from ..database.db import Database
from ..models import PlaylistItem, SyncAction, SyncActionType
from ..scanner.playlist_scanner import PlaylistScanner
from ..sync.filesystem import list_files
from ..utils.naming import sanitize_title
from ..utils.yt import extract_playlist_id


class SyncService:
    """High-level orchestration for a single playlist sync pass.

    The service pulls the latest remote playlist snapshot, persists the
    playlist and item metadata in the database, and compares the remote state
    with the local filesystem to produce sync actions.
    """

    def __init__(self, db: Database) -> None:
        self.db = db
        self.scanner = PlaylistScanner()

    def _mode_to_extensions(self, mode: str) -> list[str]:
        if mode == "audio":
            return [".mp3"]
        if mode == "video":
            return [".mp4"]
        if mode == "both":
            return [".mp3", ".mp4"]
        return [".mp4"]

    def _compute_actions(
        self,
        remote: Sequence[PlaylistItem],
        db_index: Mapping[str, PlaylistItem],
        fs_entries: Iterable[Path],
        extension: str,
    ) -> List[SyncAction]:
        """Compare remote items, database state, and filesystem to produce actions.
        
        Computes DOWNLOAD/RENAME/DELETE based on the filename scheme "0001 - Title.ext".
        """
        actions: List[SyncAction] = []

        desired_names = {
            item.video_id: f"{item.playlist_index:04d} - {item.title}{extension}"
            for item in remote
        }

        fs_by_name = {p.name: p for p in fs_entries}

        for item in remote:
            desired_name = desired_names[item.video_id]
            # If DB knows the current local filename and it already matches and exists -> nothing to do
            if item.local_filename == desired_name and desired_name in fs_by_name:
                continue

            # If DB knows a different current filename and it exists -> plan a rename
            if item.local_filename and item.local_filename in fs_by_name and item.local_filename != desired_name:
                actions.append(
                    SyncAction(
                        SyncActionType.RENAME,
                        item=item,
                        from_name=item.local_filename,
                        to_name=desired_name,
                    )
                )
                continue

            # If the desired file already exists on disk but DB doesn't reflect it -> skip (already correct)
            if desired_name in fs_by_name:
                actions.append(SyncAction(SyncActionType.SKIP, item=item, to_name=desired_name))
                continue

            # Otherwise, we need to download
            actions.append(SyncAction(SyncActionType.DOWNLOAD, item=item, to_name=desired_name))

        known_ids = {i.video_id for i in remote}
        for vid, db_item in db_index.items():
            if vid not in known_ids and db_item.local_filename:
                actions.append(SyncAction(SyncActionType.DELETE, item=db_item, from_name=db_item.local_filename))

        return actions

    def sync_from_config(self, playlist_cfg: dict) -> List[SyncAction]:
        """Return the sync actions required to bring one playlist in sync.

        This method does not apply any changes itself. It normalizes the
        configuration, refreshes the playlist/item records in SQLite, and then
        computes the actions needed for the configured download mode.
        """
        url: str = playlist_cfg.get("url")
        mode: str = playlist_cfg.get("download_mode", "video")
        save_path = Path(playlist_cfg.get("save_path", "./downloads")).resolve()
        save_path.mkdir(parents=True, exist_ok=True)

        playlist_id = extract_playlist_id(url) or url
        # Ensure playlist row exists/updated
        self.db.upsert_playlist(
            id=playlist_id,
            name=playlist_cfg.get("name"),
            url=url,
            path=str(save_path),
            mode=mode,
            auto_sync=int(bool(playlist_cfg.get("auto_sync", False))),
            sync_interval_minutes=int(playlist_cfg.get("sync_interval_minutes", 0) or 0),
        )
        ffmpeg_cfg = playlist_cfg.get("ffmpeg_path")
        items = self.scanner.scan(url, playlist_id, ffmpeg_path=str(ffmpeg_cfg) if ffmpeg_cfg is not None else None)

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

        # Augment remote items with DB-known filenames/download flags
        augmented: List[PlaylistItem] = []
        for it in sanitized:
            known = db_index.get(it.video_id)
            if known is None:
                augmented.append(it)
            else:
                augmented.append(
                    PlaylistItem(
                        playlist_id=it.playlist_id,
                        video_id=it.video_id,
                        title=it.title,
                        playlist_index=it.playlist_index,
                        local_filename=known.local_filename,
                        downloaded=known.downloaded,
                    )
                )

        exts = self._mode_to_extensions(mode)
        merged_actions: List[SyncAction] = []

        # Compute per-extension actions against respective roots
        for ext in exts:
            if ext == ".mp3":
                fs = list_files(save_path / "audio", [".mp3"])
            elif ext == ".mp4":
                fs = list_files(save_path / "video", [".mp4"])
            else:
                fs = list_files(save_path, [ext])
            actions = self._compute_actions(augmented, db_index, fs, ext)
            merged_actions.extend(actions)

        return merged_actions
