from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class _SmoothWheelFilter(QtCore.QObject):
    def __init__(self, area: QtWidgets.QAbstractScrollArea, *, duration_ms: int = 140) -> None:
        super().__init__(area)
        self._area = area
        self._duration_ms = max(60, int(duration_ms))
        self._anim = QtCore.QPropertyAnimation(area.verticalScrollBar(), b"value", self)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:  # noqa: N802
        if event.type() != QtCore.QEvent.Type.Wheel:
            return super().eventFilter(obj, event)

        wheel = event  # type: ignore[assignment]
        try:
            angle_y = wheel.angleDelta().y()
            pixel_y = wheel.pixelDelta().y()
        except Exception:
            return super().eventFilter(obj, event)

        dy = pixel_y if pixel_y else angle_y
        if dy == 0:
            return True

        sb = self._area.verticalScrollBar()
        start = sb.value()

        # Map a wheel "step" to a reasonable pixel delta; keep it snappy but not jarring.
        base_step = 80
        if pixel_y:
            delta = -dy
        else:
            delta = int(round(-dy / 120.0 * base_step))

        target = max(sb.minimum(), min(sb.maximum(), start + delta))
        if target == start:
            return True

        self._anim.stop()
        self._anim.setDuration(self._duration_ms)
        self._anim.setStartValue(start)
        self._anim.setEndValue(target)
        self._anim.start()
        return True


def enable_smooth_scrolling(widget: QtWidgets.QAbstractScrollArea, *, duration_ms: int = 140) -> None:
    """
    Enables animated wheel scrolling for QAbstractScrollArea-derived widgets
    (QListWidget, QTableWidget, QPlainTextEdit, etc.).
    """
    filt = _SmoothWheelFilter(widget, duration_ms=duration_ms)
    widget.viewport().installEventFilter(filt)
    # Keep a reference to avoid the filter being GC'd.
    widget.setProperty("_smooth_wheel_filter", filt)

