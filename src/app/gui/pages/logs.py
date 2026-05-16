from __future__ import annotations

import json

from PySide6 import QtWidgets

from ..smooth_scroll import enable_smooth_scrolling


class LogsPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Logs")
        title.setObjectName("pageTitle")

        top = QtWidgets.QHBoxLayout()
        top.addWidget(title)
        top.addStretch(1)
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self._clear)
        top.addWidget(clear_btn)
        layout.addLayout(top)

        self._text = QtWidgets.QPlainTextEdit()
        self._text.setReadOnly(True)
        enable_smooth_scrolling(self._text)
        layout.addWidget(self._text, 1)

    def _clear(self) -> None:
        self._text.clear()

    def on_event(self, name: str, payload: dict) -> None:
        # Avoid flooding the UI with high-frequency progress updates.
        if name == "DownloadProgress":
            return
        # Keep this lightweight: append a single-line JSON entry.
        try:
            line = json.dumps({"event": name, **payload}, ensure_ascii=False)
        except Exception:
            line = f"{name}: {payload}"
        self._text.appendPlainText(line)
        self._text.moveCursor(self._text.textCursor().End)
