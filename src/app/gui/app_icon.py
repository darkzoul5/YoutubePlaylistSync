from __future__ import annotations

import sys
from pathlib import Path

from PySide6 import QtGui, QtWidgets


def _resource_base() -> Path:
    # PyInstaller sets sys._MEIPASS to the temp extraction dir.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(str(base))
    return Path.cwd()


def load_app_icon() -> QtGui.QIcon:
    """
    Best-effort app icon loader.

    Looks for `assets/icon.png` in the current working directory (dev),
    or in the PyInstaller bundle root (packaged).
    """
    candidates = [
        Path("assets/icon.png"),
        _resource_base() / "assets" / "icon.png",
    ]
    for p in candidates:
        try:
            if p.exists():
                icon = QtGui.QIcon(str(p))
                if not icon.isNull():
                    return icon
        except Exception:
            pass

    # Fallback to a platform theme icon (Linux) or a generic icon.
    try:
        themed = QtGui.QIcon.fromTheme("applications-multimedia")
        if not themed.isNull():
            return themed
    except Exception:
        pass

    return QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)

