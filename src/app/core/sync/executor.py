from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Iterable, List

from ..download.queue_manager import DownloadJob, QueueManager
from ..download.workers import default_worker
from ..models import SyncAction, SyncActionType
from ..sync.reorder import safe_multi_rename


class ActionExecutor:
    def __init__(self, concurrency: int = 2) -> None:
        self.concurrency = max(1, concurrency)

    async def execute(self, actions: Iterable[SyncAction], playlist_cfg: dict) -> None:
        save_path = Path(playlist_cfg.get("save_path", "./downloads")).resolve()
        mode = playlist_cfg.get("download_mode", "audio")

        # Prepare roots
        audio_root = save_path / "audio"
        video_root = save_path / "video"
        audio_root.mkdir(parents=True, exist_ok=True)
        video_root.mkdir(parents=True, exist_ok=True)

        # First, handle renames safely in batch per extension
        await self._apply_renames(actions, audio_root, video_root)

        # Then, recycle deletions
        self._apply_deletions(actions, audio_root, video_root)

        # Finally, perform downloads concurrently
        await self._apply_downloads(actions, mode, audio_root, video_root)

    async def _apply_renames(self, actions: Iterable[SyncAction], audio_root: Path, video_root: Path) -> None:
        audio_renames = []
        video_renames = []
        for a in actions:
            if a.type != SyncActionType.RENAME or not a.from_name or not a.to_name:
                continue
            if a.to_name.endswith(".mp3"):
                audio_renames.append((audio_root / a.from_name, audio_root / a.to_name))
            elif a.to_name.endswith(".mp4"):
                video_renames.append((video_root / a.from_name, video_root / a.to_name))

        if audio_renames:
            safe_multi_rename(audio_renames)
        if video_renames:
            safe_multi_rename(video_renames)

    def _apply_deletions(self, actions: Iterable[SyncAction], audio_root: Path, video_root: Path) -> None:
        recycle_audio = audio_root.parent / ".recycle" / "audio"
        recycle_video = video_root.parent / ".recycle" / "video"
        recycle_audio.mkdir(parents=True, exist_ok=True)
        recycle_video.mkdir(parents=True, exist_ok=True)

        for a in actions:
            if a.type != SyncActionType.DELETE or not a.from_name:
                continue
            if a.from_name.endswith(".mp3"):
                src = audio_root / a.from_name
                dst = recycle_audio / a.from_name
            else:
                src = video_root / a.from_name
                dst = recycle_video / a.from_name
            if src.exists():
                try:
                    if dst.exists():
                        dst.unlink()
                    shutil.move(str(src), str(dst))
                except Exception:
                    # fallback to delete if move fails
                    try:
                        src.unlink()
                    except Exception:
                        pass

    async def _apply_downloads(self, actions: Iterable[SyncAction], mode: str, audio_root: Path, video_root: Path) -> None:
        queue = QueueManager(concurrency=self.concurrency)

        async def worker(job: DownloadJob):
            await default_worker(job)

        await queue.start(worker)
        try:
            for a in actions:
                if a.type != SyncActionType.DOWNLOAD or not a.item or not a.to_name:
                    continue
                is_audio = a.to_name.endswith(".mp3")
                root = audio_root if is_audio else video_root
                output_path = root / a.to_name
                output_path.parent.mkdir(parents=True, exist_ok=True)
                url = f"https://www.youtube.com/watch?v={a.item.video_id}"
                job = DownloadJob(item=a.item, output_path=output_path, url=url, mode=("audio" if is_audio else "video"))
                await queue.enqueue(job)
        finally:
            await queue._queue.join()  # wait for all jobs
            await queue.stop()
