from __future__ import annotations
from typing import Any, Dict
from PySide6 import QtCore

from ..core.events.event_bus import EventBus


class BusBridge(QtCore.QObject):
    """
    Bridges backend EventBus async events onto the Qt main thread.

    Emits `event(name, payload)` as a Qt signal, thread-safe.
    """

    event = QtCore.Signal(str, dict)

    def __init__(self, bus: EventBus, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._bus = bus

        for name in (
            "SyncStarted",
            "SyncSummary",
            "SyncFinished",
            "DownloadStarted",
            "DownloadProgress",
            "DownloadCompleted",
            "DownloadFailed",
            "RenameApplied",
            "FileRecycled",
        ):
            self._bus.subscribe(name, self._make_handler(name))

    def _make_handler(self, name: str):
        async def handler(payload: Dict[str, Any]) -> None:
            # Ensure delivery on the Qt main thread.
            self.event.emit(name, dict(payload))

        return handler

