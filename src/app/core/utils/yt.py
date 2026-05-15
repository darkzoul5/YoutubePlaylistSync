from __future__ import annotations

from urllib.parse import parse_qs, urlparse


def extract_playlist_id(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "list" in qs and qs.get("list"):
            return qs.get("list", [None])[0]
        return None
    except Exception:
        return None
