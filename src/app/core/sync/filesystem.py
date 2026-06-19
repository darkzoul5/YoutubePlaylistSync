from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


def list_files(root: Path, extensions: Sequence[str]) -> List[Path]:
    """List all files in root directory with given extensions."""
    exts = {e.lower() for e in extensions}
    results: List[Path] = []
    if not root.exists():
        return results
    for p in root.glob("**/*"):
        if p.is_file() and p.suffix.lower() in exts:
            results.append(p)
    return results
