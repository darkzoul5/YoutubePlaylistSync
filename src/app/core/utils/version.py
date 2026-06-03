from __future__ import annotations

import sys
from pathlib import Path


def _resource_base() -> Path:
    # PyInstaller sets sys._MEIPASS to the temp extraction dir.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(str(base))
    return Path.cwd()


def _read_text(path: Path) -> str | None:
    try:
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            return text or None
    except Exception:
        pass
    return None
def get_app_version() -> str:
    """
    Returns the packaged app version.

    In release builds this reads from `version.txt` bundled into the EXE.
    """
    candidates = [
        Path("version.txt"),
        _resource_base() / "version.txt",
    ]
    for candidate in candidates:
        text = _read_text(candidate)
        if text:
            return text

    return "dev"
