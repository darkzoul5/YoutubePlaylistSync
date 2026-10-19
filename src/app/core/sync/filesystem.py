from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ..models import FilesystemEntry


def list_files(root: Path, extensions: Sequence[str]) -> list[FilesystemEntry]:
    exts = {e.lower() for e in extensions}
    results: list[FilesystemEntry] = []
    if not root.exists():
        return results
    for p in root.glob("**/*"):
        if p.is_file() and p.suffix.lower() in exts:
            results.append(FilesystemEntry(name=p.name, path=p))
    return results
