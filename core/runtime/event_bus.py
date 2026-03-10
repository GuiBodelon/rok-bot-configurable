from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from time import time
from typing import Any, Callable, DefaultDict, Dict, List, Optional
from uuid import uuid4

EventHandler = Callable[["RuntimeEvent"], None]


@dataclass(frozen=True)
class RuntimeEvent:
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)
    event_id: str = field(default_factory=lambda: str(uuid4()))


class EventBus:
    """
    Barramento simples de eventos em memória.

    Responsabilidades:
    - registrar listeners por nome de evento
    - emitir eventos
    - permitir unsubscribe
    - suportar wildcard '*' para observadores globais
    """

    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[EventHandler]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, event_name: str, handler: EventHandler) -> Callable[[], None]:
        with self._lock:
            self._listeners[event_name].append(handler)

        def unsubscribe() -> None:
            self.unsubscribe(event_name, handler)

        return unsubscribe

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        with self._lock:
            listeners = self._listeners.get(event_name, [])
            if handler in listeners:
                listeners.remove(handler)

            if not listeners and event_name in self._listeners:
                del self._listeners[event_name]

    def emit(
        self, event_name: str, payload: Optional[Dict[str, Any]] = None
    ) -> RuntimeEvent:
        event = RuntimeEvent(
            name=event_name,
            payload=payload or {},
        )

        listeners = self._get_handlers_for_event(event_name)

        for handler in listeners:
            handler(event)

        return event

    def clear(self) -> None:
        with self._lock:
            self._listeners.clear()

    def listener_count(self, event_name: str | None = None) -> int:
        with self._lock:
            if event_name is not None:
                return len(self._listeners.get(event_name, []))

            return sum(len(handlers) for handlers in self._listeners.values())

    def registered_events(self) -> List[str]:
        with self._lock:
            return sorted(self._listeners.keys())

    def _get_handlers_for_event(self, event_name: str) -> List[EventHandler]:
        with self._lock:
            specific_handlers = list(self._listeners.get(event_name, []))
            wildcard_handlers = list(self._listeners.get("*", []))

        return specific_handlers + wildcard_handlers
