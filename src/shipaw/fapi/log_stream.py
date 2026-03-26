from __future__ import annotations

import asyncio
import html
from collections import deque
from typing import AsyncIterator, TYPE_CHECKING, Any

LogLineTup = tuple[str, str]

if TYPE_CHECKING:
    from loguru import Message
else:
    Message = Any


class LogStream:
    def __init__(self, max_history: int = 300, queue_size: int = 200) -> None:
        self._history: deque[LogLineTup] = deque(maxlen=max_history)
        self._subscribers: set[asyncio.Queue[LogLineTup]] = set()
        self._queue_size = queue_size

    def sink(self, message: Message) -> None:
        rec = message.record
        level_name = rec["level"].name.lower()
        line = f"{rec['time']:%H:%M:%S} | {rec['level'].name:<8} | {rec['message']}"
        self._history.append((level_name, line))
        dead: list[asyncio.Queue[LogLineTup]] = []
        for q in self._subscribers:
            try:
                q.put_nowait((level_name, line))
            except asyncio.QueueFull:
                # Drop if a client is too slow; keep app logging non-blocking.
                pass
            except RuntimeError:
                dead.append(q)

        for q in dead:
            self._subscribers.discard(q)

    async def stream(self, replay: int = 80) -> AsyncIterator[str]:
        q: asyncio.Queue[LogLineTup] = asyncio.Queue(maxsize=self._queue_size)
        self._subscribers.add(q)

        try:
            # Replay recent history when client connects.
            for level_name, line in list(self._history)[-replay:]:
                safe = html.escape(line)
                yield f"event: log\ndata: <div class='log-line log-{level_name}'>{safe}</div>\n\n"

            while True:
                try:
                    level_name, line = await asyncio.wait_for(q.get(), timeout=15)
                    safe = html.escape(line)
                    yield f"event: log\ndata: <div class='log-line log-{level_name}'>{safe}</div>\n\n"
                except TimeoutError:
                    # Keep connection alive
                    yield ': ping\n\n'
        finally:
            self._subscribers.discard(q)
