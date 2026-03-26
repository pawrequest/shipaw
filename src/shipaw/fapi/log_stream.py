from __future__ import annotations

import asyncio
import html
from collections import deque
from typing import AsyncIterator, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from loguru import Message
else:
    Message = Any


class LogStream:
    def __init__(self, max_history: int = 300, queue_size: int = 200) -> None:
        self._history: deque[str] = deque(maxlen=max_history)
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._queue_size = queue_size

    def sink(self, message: Message) -> None:
        rec = message.record
        line = f"{rec['time']:%H:%M:%S} | {rec['level'].name:<8} | {rec['message']}"
        self._history.append(line)

        dead: list[asyncio.Queue[str]] = []
        for q in self._subscribers:
            try:
                q.put_nowait(line)
            except asyncio.QueueFull:
                # Drop if a client is too slow; keep app logging non-blocking.
                pass
            except RuntimeError:
                dead.append(q)

        for q in dead:
            self._subscribers.discard(q)

    async def stream(self, replay: int = 80) -> AsyncIterator[str]:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=self._queue_size)
        self._subscribers.add(q)

        try:
            # Replay recent history when client connects.
            for line in list(self._history)[-replay:]:
                safe = html.escape(line)
                yield f"event: log\ndata: <div class='log-line'>{safe}</div>\n\n"

            while True:
                try:
                    line = await asyncio.wait_for(q.get(), timeout=15)
                    safe = html.escape(line)
                    yield f"event: log\ndata: <div class='log-line'>{safe}</div>\n\n"
                except TimeoutError:
                    # Keep connection alive
                    yield ': ping\n\n'
        finally:
            self._subscribers.discard(q)
