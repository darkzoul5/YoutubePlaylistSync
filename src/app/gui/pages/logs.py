from __future__ import annotations

import json

from PySide6 import QtCore, QtWidgets

from ..smooth_scroll import enable_smooth_scrolling


class LogsPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("logsPage")
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

        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setObjectName("logsScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self._entries = QtWidgets.QWidget()
        self._entries.setObjectName("logEntries")
        self._entries_layout = QtWidgets.QVBoxLayout(self._entries)
        self._entries_layout.setContentsMargins(2, 2, 2, 2)
        self._entries_layout.setSpacing(8)
        self._entries_layout.addStretch(1)
        self._scroll.setWidget(self._entries)
        enable_smooth_scrolling(self._scroll)
        layout.addWidget(self._scroll, 1)

    def _clear(self) -> None:
        while self._entries_layout.count() > 1:
            item = self._entries_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def on_event(self, name: str, payload: dict) -> None:
        # Avoid flooding the UI with high-frequency progress updates.
        if name == "DownloadProgress":
            return
        # Keep the event name in the header and show only its payload here.
        try:
            line = json.dumps(payload, ensure_ascii=False)
        except Exception:  # noqa: BLE001 - fall back to a readable representation
            line = str(payload)
        entry = QtWidgets.QFrame()
        entry.setObjectName("logEntry")

        entry_layout = QtWidgets.QVBoxLayout(entry)
        entry_layout.setContentsMargins(12, 9, 12, 9)
        entry_layout.setSpacing(4)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        event_label = QtWidgets.QLabel(name)
        event_label.setObjectName("logEventName")
        event_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        header_layout.addWidget(event_label)
        header_layout.addStretch(1)

        copy_btn = QtWidgets.QPushButton("Copy")
        copy_btn.setToolTip("Copy this log entry")
        copy_btn.clicked.connect(lambda: self._copy_entry(f"{name}\n{line}"))
        header_layout.addWidget(copy_btn)
        entry_layout.addLayout(header_layout)

        body_label = QtWidgets.QLabel(line)
        body_label.setObjectName("logEntryBody")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        body_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        entry_layout.addWidget(body_label)

        self._entries_layout.insertWidget(self._entries_layout.count() - 1, entry)
        self._scroll.verticalScrollBar().setValue(self._scroll.verticalScrollBar().maximum())

    @staticmethod
    def _copy_entry(text: str) -> None:
        QtWidgets.QApplication.clipboard().setText(text)
