from __future__ import annotations

"""
Entry point for the new backend (no GUI). For now, this only verifies
that configuration and database setup work. Future iterations will wire
up scanner, diff engine, queue, and scheduler.
"""

from pathlib import Path

from .config.settings import Settings
from .core.database.db import Database
from .core.sync.service import SyncService


def bootstrap(db_path: Path | None = None) -> None:
    settings = Settings()
    db = Database((db_path or Path("app/data/app.db")).resolve())
    service = SyncService(db)

    # Iterate configured playlists and compute actions (no execution yet)
    for pl in settings.playlists:
        try:
            actions = service.sync_from_config(pl)
            # For now, just print summary for visibility during development
            print(f"Computed {len(actions)} actions for playlist: {pl.get('url')}")
        except Exception as exc:  # keep bootstrap resilient during early dev
            print(f"Failed to sync playlist {pl.get('url')}: {exc}")


if __name__ == "__main__":
    bootstrap()
