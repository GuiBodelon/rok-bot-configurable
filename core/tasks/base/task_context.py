from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime import EventBus, StateStore


@dataclass(slots=True)
class TaskContext:
    """
    Provides the runtime dependencies and metadata required by a task.

    This object is intentionally lightweight and framework-agnostic.
    It gives tasks access to the current profile, runtime state, event bus,
    and optional low-level services that will be connected later.
    """

    profile: Dict[str, Any]
    state_store: StateStore
    event_bus: EventBus
    vision_service: Optional[Any] = None
    input_service: Optional[Any] = None
    guard_service: Optional[Any] = None
    cooldown_service: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None

    def get_task_config(self, task_id: str) -> Dict[str, Any]:
        """
        Returns the configuration block for the given task.

        If the task does not exist in the profile, an empty dictionary
        is returned.
        """
        tasks = self.profile.get("tasks", {})
        task_config = tasks.get(task_id, {})
        return task_config if isinstance(task_config, dict) else {}

    def emit(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Emits a runtime event through the shared event bus.
        """
        self.event_bus.emit(event_name, payload or {})

    def get_runtime_state(self) -> Dict[str, Any]:
        """
        Returns the current runtime state as a dictionary snapshot.
        """
        return self.state_store.to_dict()
