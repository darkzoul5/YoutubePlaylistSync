from __future__ import annotations


def is_youtube_rate_limit_error(message: str | None) -> bool:
    """
    Best-effort detection of YouTube "bot check" / auth-gated extraction failures.

    yt-dlp typically surfaces this as:
      - "Sign in to confirm you’re not a bot"
      - mentions of --cookies / --cookies-from-browser
    """
    if not message:
        return False
    s = str(message).lower()
    needles = [
        "sign in to confirm",
        "you're not a bot",
        "you’re not a bot",
        "--cookies-from-browser",
        "--cookies",
    ]
    return any(n in s for n in needles)

