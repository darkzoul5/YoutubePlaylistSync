from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DownloadMode(str, Enum):
    audio = "audio"
    video = "video"
    both = "both"


@dataclass(frozen=True)
class Playlist:
    id: str
    name: str | None
    url: str
    path: Path
    mode: DownloadMode = DownloadMode.audio
    auto_sync: bool = False
    sync_interval_minutes: int = 0


@dataclass(frozen=True)
class PlaylistItem:
    playlist_id: str
    video_id: str
    title: str
    playlist_index: int
    local_filename: str | None = None
    downloaded: bool = False


class SyncActionType(str, Enum):
    DOWNLOAD = "DOWNLOAD"
    DELETE = "DELETE"
    RENAME = "RENAME"
    REORDER = "REORDER"
    SKIP = "SKIP"
    REPAIR = "REPAIR"


@dataclass(frozen=True)
class SyncAction:
    type: SyncActionType
    item: PlaylistItem | None = None
    from_name: str | None = None
    to_name: str | None = None


@dataclass(frozen=True)
class FilesystemEntry:
    name: str
    path: Path
