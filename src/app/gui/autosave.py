from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterator

from PySide6 import QtCore


class DebouncedAutosave(QtCore.QObject):
    """Small helper for debounced autosave flows in Qt widgets."""

    def __init__(self, parent: QtCore.QObject, callback: Callable[[], None], interval_ms: int = 600) -> None:
        super().__init__(parent)
        self._suppressed = False
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(callback)

    @contextmanager
    def suppressed(self) -> Iterator[None]:
        previous = self._suppressed
        self._suppressed = True
        try:
            yield
        finally:
            self._suppressed = previous

    def set_suppressed(self, suppressed: bool) -> None:
        self._suppressed = bool(suppressed)

    def schedule(self, *, enabled: bool = True) -> None:
        if self._suppressed or not enabled:
            return
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()