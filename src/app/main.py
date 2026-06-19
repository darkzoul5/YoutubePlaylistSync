"""
Entry point for the backend (no GUI).

For now, this verifies configuration + database setup and can run a one-off sync.
Future iterations will wire up scheduler and a GUI.
"""

from __future__ import annotations

from pathlib import Path

from .core.sync.runner import build_sync_stack, format_action_summary, run_sync_batch


def bootstrap(db_path: Path | None = None) -> None:
    settings, db, service, executor = build_sync_stack(db_path)

    def on_plan(pl: dict, playlist_id: str, actions, counts: dict[str, int]) -> None:
        del playlist_id
        print(f"Applying {len(actions)} actions for: {pl.get('url')}")
        print(f"Plan → {format_action_summary(counts)}")

    def on_no_actions(pl: dict, playlist_id: str) -> None:
        del playlist_id
        print(f"No actions needed for: {pl.get('url')}")

    def on_applied(pl: dict, playlist_id: str) -> None:
        del pl, playlist_id
        print("Applied actions.")

    def on_import_error(pl: dict, exc: Exception) -> bool:
        print(f"Failed to sync playlist {pl.get('url')}: {exc}")
        return True

    def on_dependency_error(pl: dict, exc: Exception) -> bool:
        del pl
        print(f"ERROR: {exc}")
        return True

    run_sync_batch(
        settings.playlists,
        db=db,
        service=service,
        executor=executor,
        apply=True,
        on_plan=on_plan,
        on_no_actions=on_no_actions,
        on_applied=on_applied,
        on_import_error=on_import_error,
        on_dependency_error=on_dependency_error,
    )


if __name__ == "__main__":
    bootstrap()
