from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Callable, Sequence

from ..database.db import Database
from ..events.event_bus import EventBus
from ..models import SyncAction
from ..utils.deps import DependencyError
from ..utils.yt import extract_playlist_id
from .executor import ActionExecutor
from .service import SyncService
from ...config.settings import Settings


def build_sync_stack(db_path: Path | None = None, *, event_bus: EventBus | None = None) -> tuple[Settings, Database, SyncService, ActionExecutor]:
    settings = Settings()
    db = Database((db_path or Path("db/app.db")).resolve())
    service = SyncService(db)
    executor = ActionExecutor(db, event_bus=event_bus)
    return settings, db, service, executor


def format_action_summary(counts: dict[str, int]) -> str:
    return ", ".join(f"{name}:{count}" for name, count in sorted(counts.items()))


def run_sync_batch(
    playlists: Sequence[dict[str, Any]],
    *,
    db: Database,
    service: SyncService,
    executor: ActionExecutor,
    apply: bool,
    on_plan: Callable[[dict[str, Any], str, list[SyncAction], dict[str, int]], None] | None = None,
    on_no_actions: Callable[[dict[str, Any], str], None] | None = None,
    on_applied: Callable[[dict[str, Any], str], None] | None = None,
    on_import_error: Callable[[dict[str, Any], Exception], bool] | None = None,
    on_dependency_error: Callable[[dict[str, Any], Exception], bool] | None = None,
) -> int:
    for playlist_cfg in playlists:
        playlist_url = str(playlist_cfg.get("url") or "")
        playlist_id = extract_playlist_id(playlist_url) or playlist_url

        try:
            actions = service.sync_from_config(playlist_cfg)
        except ImportError as exc:
            if on_import_error is not None and on_import_error(playlist_cfg, exc):
                continue
            return 2

        counts: dict[str, int] = {}
        for action in actions:
            counts[action.type.name] = counts.get(action.type.name, 0) + 1

        if on_plan is not None:
            on_plan(playlist_cfg, playlist_id, actions, counts)

        if apply and actions:
            try:
                asyncio.run(executor.execute(actions, playlist_cfg))
            except DependencyError as exc:
                if on_dependency_error is not None and on_dependency_error(playlist_cfg, exc):
                    continue
                return 2
            db.set_playlist_last_sync(playlist_id)
            if on_applied is not None:
                on_applied(playlist_cfg, playlist_id)
        elif on_no_actions is not None:
            on_no_actions(playlist_cfg, playlist_id)

    return 0