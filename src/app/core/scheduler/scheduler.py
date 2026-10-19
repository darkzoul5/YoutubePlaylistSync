from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import timedelta


class Scheduler:
    """
    Lightweight placeholder for background scheduling. This can later be
    swapped for APScheduler without changing call sites.
    """

    def __init__(self) -> None:
        self._jobs: list[tuple[timedelta, Callable[[], Awaitable[None]]]] = []

    def every(self, interval: timedelta, coro_factory: Callable[[], Awaitable[None]]):
        self._jobs.append((interval, coro_factory))
        return self

    # A full implementation will run an event loop and await jobs.
