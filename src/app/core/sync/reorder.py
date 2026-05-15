from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple


def safe_multi_rename(renames: Iterable[Tuple[Path, Path]]) -> None:
    """
    Apply multiple renames safely using a two-pass strategy to avoid
    name collisions. Each item is a tuple (src_path, dst_path).
    """
    temp_suffix = ".renametemp"
    planned = list(renames)
    existing_dests = {dst for _, dst in planned}

    # Pass 1: move all sources that would collide to temporary names
    temps: Dict[Path, Path] = {}
    for src, dst in planned:
        if not src.exists():
            continue
        if src.name == dst.name:
            continue
        # If destination exists or another source will become destination, use temp
        if dst.exists() or dst in existing_dests:
            tmp = src.with_suffix(src.suffix + temp_suffix)
            # Ensure unique temp
            i = 0
            while tmp.exists():
                i += 1
                tmp = src.with_name(src.name + f".{i}" + temp_suffix)
            src.rename(tmp)
            temps[tmp] = dst
        else:
            # direct rename safe
            src.rename(dst)

    # Pass 2: move all temp files to their final destinations
    for tmp, dst in temps.items():
        if not tmp.exists():
            continue
        if dst.exists():
            dst.unlink()
        tmp.rename(dst)
