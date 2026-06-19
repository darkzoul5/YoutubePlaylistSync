from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .core.events.event_bus import EventBus
import re
from .core.sync.runner import build_sync_stack, format_action_summary, run_sync_batch
from .core.utils.logging_setup import configure_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="YouTube Playlist Sync — compute/apply actions")
    parser.add_argument("--apply", action="store_true", help="Apply actions (otherwise compute-only)")
    parser.add_argument("--db", type=Path, default=Path("db/app.db"), help="Path to SQLite database")
    parser.add_argument("--playlist", type=int, default=None, help="Only run for a specific playlist index (0-based)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed events (rename/recycle/start)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging to console + app/data/app.log")
    args = parser.parse_args(argv)

    configure_logging(verbose=bool(args.debug), log_file=Path("app/data/app.log"))
    log = logging.getLogger(__name__)

    bus = EventBus()
    settings, db, service, executor = build_sync_stack(args.db, event_bus=bus)

    seen_errors: set[str] = set()

    ansi = re.compile(r"\x1b\[[0-9;]*m")

    async def on_started(payload):
        if args.verbose:
            vid = payload.get("video_id")
            target = payload.get("target")
            print(f"START: {vid} → {target}")

    async def on_completed(payload):
        vid = payload.get("video_id")
        target = payload.get("target")
        print(f"OK: {vid} → {target}")

    async def on_failed(payload):
        raw = str(payload.get("error", "failed"))
        msg = ansi.sub("", raw)
        # Print only once per unique message
        if msg not in seen_errors:
            seen_errors.add(msg)
            # Friendly hint for missing ffmpeg
            if "ffmpeg not found" in msg.lower():
                print("ERROR: ffmpeg not found. Install ffmpeg or set 'ffmpeg_path' in config.")
            else:
                print(f"ERROR: {msg}")

    # Subscribe to key events
    bus.subscribe("DownloadStarted", on_started)
    bus.subscribe("DownloadCompleted", on_completed)
    bus.subscribe("DownloadFailed", on_failed)
    if args.verbose:
        async def on_rename(payload):
            print(f"RENAME: {payload.get('video_id')} → {payload.get('to')}")
        async def on_recycle(payload):
            print(f"RECYCLE: {payload.get('video_id')} ← {payload.get('name')}")
        bus.subscribe("RenameApplied", on_rename)
        bus.subscribe("FileRecycled", on_recycle)

    selected_playlists = settings.playlists
    if args.playlist is not None:
        selected_playlists = [selected_playlists[args.playlist]] if 0 <= args.playlist < len(selected_playlists) else []

    def on_plan(pl: dict, playlist_id: str, actions, counts: dict[str, int]) -> None:
        summary = format_action_summary(counts)
        print(f"Playlist {playlist_id}: {len(actions)} actions → {summary}")
        log.info("playlist=%s actions=%s summary=%s", playlist_id, len(actions), summary)

    def on_no_actions(pl: dict, playlist_id: str) -> None:
        del pl
        print(f"Playlist {playlist_id}: 0 actions →")
        log.info("playlist=%s actions=0 summary=", playlist_id)

    def on_applied(pl: dict, playlist_id: str) -> None:
        del pl
        print(f"Applied actions for {playlist_id}.")
        log.info("playlist=%s applied_actions=done", playlist_id)

    def on_import_error(pl: dict, exc: Exception) -> bool:
        del pl
        msg = str(exc)
        if "yt_dlp" in msg or "yt-dlp" in msg:
            print("yt-dlp Python package is required. Install with: pip install -U yt-dlp")
        else:
            print(f"ERROR: {exc}")
        return False

    def on_dependency_error(pl: dict, exc: Exception) -> bool:
        del pl
        print(f"ERROR: {exc}")
        log.error("dependency error: %s", exc)
        return False

    return run_sync_batch(
        selected_playlists,
        db=db,
        service=service,
        executor=executor,
        apply=bool(args.apply),
        on_plan=on_plan,
        on_no_actions=on_no_actions,
        on_applied=on_applied,
        on_import_error=on_import_error,
        on_dependency_error=on_dependency_error,
    )


if __name__ == "__main__":
    raise SystemExit(main())
