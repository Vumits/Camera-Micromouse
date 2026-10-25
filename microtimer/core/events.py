from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def on(self, event_name: str, handler: Callable[[Any], None]) -> None:
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, payload: Any = None) -> None:
        for handler in self._handlers[event_name]:
            handler(payload)
