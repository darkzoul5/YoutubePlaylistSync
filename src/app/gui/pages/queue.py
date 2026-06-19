from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ..smooth_scroll import enable_smooth_scrolling


class QueuePage(QtWidgets.QWidget):
    cancel_sync_requested = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("queuePage")
        # Map (playlist_id, video_id) to a stable item; its `.row()` tracks sorting moves.
        self._rows_by_key: dict[tuple[str, str], QtWidgets.QTableWidgetItem] = {}
        self._pending_by_key: dict[tuple[str, str], dict] = {}
        self._playlist_labels: dict[str, str] = {}

        self._flush_timer = QtCore.QTimer(self)
        self._flush_timer.setInterval(150)
        self._flush_timer.timeout.connect(self._flush_pending)
        self._flush_timer.start()

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Queue")
        title.setObjectName("pageTitle")

        top = QtWidgets.QHBoxLayout()
        top.addWidget(title)
        top.addStretch(1)
        clear_btn = QtWidgets.QPushButton("Clear completed")
        clear_btn.clicked.connect(self._clear_completed)
        cancel_btn = QtWidgets.QPushButton("Cancel all")
        cancel_btn.clicked.connect(self.cancel_sync_requested.emit)
        top.addWidget(clear_btn)
        top.addWidget(cancel_btn)
        layout.addLayout(top)

        self._table = QtWidgets.QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(["Playlist", "Video ID", "Status", "Progress", "Speed", "ETA", "Target/File"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setSortingEnabled(True)
        self._table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        enable_smooth_scrolling(self._table)
        layout.addWidget(self._table, 1)

        self._hint = QtWidgets.QLabel("Waiting for downloads…")
        layout.addWidget(self._hint)

    def on_event(self, name: str, payload: dict) -> None:
        if name not in {"DownloadStarted", "DownloadProgress", "DownloadCompleted", "DownloadFailed"}:
            return
        vid = str(payload.get("video_id") or "")
        if not vid:
            return
        pid = str(payload.get("playlist_id") or "")
        key = (pid, vid)

        latest = dict(payload)
        latest["_event"] = name
        self._pending_by_key[key] = latest

    def set_playlist_labels(self, labels: dict[str, str]) -> None:
        self._playlist_labels = dict(labels)
        # Update any existing rows to reflect new names.
        for row in range(self._table.rowCount()):
            pl_item = self._table.item(row, 0)
            if pl_item is None:
                continue
            pid = pl_item.data(QtCore.Qt.ItemDataRole.UserRole)
            if not pid:
                continue
            pl_item.setText(self._playlist_labels.get(str(pid), str(pid)))

    def _ensure_row(self, key: tuple[str, str]) -> int:
        vid_item = self._rows_by_key.get(key)
        if vid_item is not None and vid_item.row() >= 0:
            return int(vid_item.row())

        pid, vid = key
        row = self._table.rowCount()
        self._table.insertRow(row)

        label = self._playlist_labels.get(pid, pid)
        pl_item = QtWidgets.QTableWidgetItem(label)
        # Keep the real playlist_id even if the displayed label changes.
        pl_item.setData(QtCore.Qt.ItemDataRole.UserRole, pid)
        pl_item.setToolTip(pid)
        self._table.setItem(row, 0, pl_item)

        vid_item = QtWidgets.QTableWidgetItem(vid)
        self._table.setItem(row, 1, vid_item)

        self._table.setItem(row, 2, QtWidgets.QTableWidgetItem("queued"))
        self._table.setItem(row, 3, QtWidgets.QTableWidgetItem(""))
        self._table.setItem(row, 4, QtWidgets.QTableWidgetItem(""))
        self._table.setItem(row, 5, QtWidgets.QTableWidgetItem(""))
        self._table.setItem(row, 6, QtWidgets.QTableWidgetItem(""))
        self._rows_by_key[key] = vid_item
        return row

    def _ensure_item(self, row: int, col: int, default: str = "") -> QtWidgets.QTableWidgetItem:
        item = self._table.item(row, col)
        if item is None:
            item = QtWidgets.QTableWidgetItem(default)
            self._table.setItem(row, col, item)
        return item

    def _target_text(self, payload: dict, current: str = "") -> str:
        value = (
            payload.get("target")
            or payload.get("filename")
            or payload.get("output_path")
            or payload.get("path")
            or payload.get("to")
            or current
        )
        if not value:
            return current
        try:
            return Path(str(value)).name or str(value)
        except Exception:
            return str(value)

    @QtCore.Slot()
    def _flush_pending(self) -> None:
        if not self._pending_by_key:
            return

        pending = dict(self._pending_by_key)
        self._pending_by_key.clear()

        sorting_was_enabled = self._table.isSortingEnabled()
        if sorting_was_enabled:
            self._table.setSortingEnabled(False)

        try:
            for key, payload in pending.items():
                name = str(payload.pop("_event", ""))
                row = self._ensure_row(key)

                status_item = self._ensure_item(row, 2, "queued")
                progress_item = self._ensure_item(row, 3, "")
                speed_item = self._ensure_item(row, 4, "")
                eta_item = self._ensure_item(row, 5, "")
                target_item = self._ensure_item(row, 6, "")
                target_text = target_item.text()

                if name == "DownloadStarted":
                    status_item.setText("started")
                    target_text = self._target_text(payload, target_text)
                    if target_text:
                        target_item.setText(target_text)
                elif name == "DownloadProgress":
                    status_item.setText(str(payload.get("status") or "downloading"))
                    prog = payload.get("progress")
                    if isinstance(prog, (int, float)):
                        pct = max(0, min(100, int(round(prog * 100))))
                        bar = self._table.cellWidget(row, 3)
                        if bar is None:
                            bar = QtWidgets.QProgressBar()
                            bar.setRange(0, 100)
                            bar.setTextVisible(True)
                            self._table.setCellWidget(row, 3, bar)
                        bar.setValue(pct)
                    sp = payload.get("speed")
                    if isinstance(sp, (int, float)) and sp > 0:
                        speed_item.setText(f"{sp/1024/1024:.2f} MiB/s")
                    et = payload.get("eta")
                    if isinstance(et, (int, float)) and et >= 0:
                        eta_item.setText(f"{int(et)}s")
                    target_text = self._target_text(payload, target_text)
                    if target_text:
                        target_item.setText(target_text)
                elif name == "DownloadCompleted":
                    status_item.setText("completed")
                    target_text = self._target_text(payload, target_text)
                    if target_text:
                        target_item.setText(target_text)
                    bar = self._table.cellWidget(row, 3)
                    if bar is None:
                        bar = QtWidgets.QProgressBar()
                        bar.setRange(0, 100)
                        bar.setTextVisible(True)
                        self._table.setCellWidget(row, 3, bar)
                    bar.setValue(100)
                    speed_item.setText("")
                    eta_item.setText("")
                elif name == "DownloadFailed":
                    status_item.setText("failed")
                    self._table.removeCellWidget(row, 3)
                    progress_item.setText("")
                    speed_item.setText("")
                    eta_item.setText("")
                    err = payload.get("error")
                    if err:
                        target_item.setText(str(err))
        finally:
            if sorting_was_enabled:
                self._table.setSortingEnabled(True)

        self._hint.setText(f"{len(self._rows_by_key)} job(s) seen.")

    def _clear_completed(self) -> None:
        to_remove: list[tuple[int, tuple[str, str]]] = []
        for key, vid_item in list(self._rows_by_key.items()):
            row = int(vid_item.row())
            if row < 0:
                self._rows_by_key.pop(key, None)
                continue
            st = self._table.item(row, 2)
            if st and st.text() == "completed":
                to_remove.append((row, key))

        for row, key in sorted(to_remove, key=lambda x: x[0], reverse=True):
            self._table.removeRow(row)
            self._rows_by_key.pop(key, None)

        # Rebuild mapping since row indices/items may have shifted.
        rebuilt: dict[tuple[str, str], QtWidgets.QTableWidgetItem] = {}
        for r in range(self._table.rowCount()):
            pl_item = self._table.item(r, 0)
            v_item = self._table.item(r, 1)
            if pl_item is None or v_item is None:
                continue
            pid = pl_item.data(QtCore.Qt.ItemDataRole.UserRole) or pl_item.text()
            vid = v_item.text()
            rebuilt[(str(pid), str(vid))] = v_item
        self._rows_by_key = rebuilt
