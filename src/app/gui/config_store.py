from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class AppConfig:
    data: Dict[str, Any]
    path: Path


def load_config(path: Path) -> AppConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("config root must be a JSON object")
    return AppConfig(data=raw, path=path)


def save_config(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")


def normalize_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure basic expected shape for config dict.
    Keeps unknown keys intact.
    """
    out = dict(data)
    pls = out.get("playlists")
    if not isinstance(pls, list):
        out["playlists"] = []
    return out
