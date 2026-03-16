from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass
class RuntimeState:
    running: bool = False
    paused: bool = False
    stopping: bool = False
    current_task: Optional[str] = None
    current_action: Optional[str] = None
    screen_state: Optional[str] = None
    last_error: Optional[str] = None
    profile_name: Optional[str] = None
    active_profile_path: Optional[str] = None
    selected_tasks: List[str] = field(default_factory=list)
    cooldowns: Dict[str, float] = field(default_factory=dict)
    fail_streaks: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateStore:
    """
    Single source of truth for the runtime state.

    Responsibilities:
    - maintain the current execution state
    - allow safe reads through snapshots
    - allow partial and atomic updates
    - reset operational state without losing flexibility
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._state = RuntimeState()

    def get_state(self) -> RuntimeState:
        with self._lock:
            return deepcopy(self._state)

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return asdict(self._state)

    def reset(self) -> RuntimeState:
        with self._lock:
            self._state = RuntimeState()
            return deepcopy(self._state)

    def set_profile(
        self, profile_name: str, profile_path: str | None = None
    ) -> RuntimeState:
        with self._lock:
            self._state.profile_name = profile_name
            self._state.active_profile_path = profile_path
            return deepcopy(self._state)

    def set_running(self, value: bool) -> RuntimeState:
        with self._lock:
            self._state.running = value
            if value:
                self._state.stopping = False
            return deepcopy(self._state)

    def set_paused(self, value: bool) -> RuntimeState:
        with self._lock:
            self._state.paused = value
            return deepcopy(self._state)

    def set_stopping(self, value: bool) -> RuntimeState:
        with self._lock:
            self._state.stopping = value
            if value:
                self._state.running = False
            return deepcopy(self._state)

    def set_current_task(self, task_name: str | None) -> RuntimeState:
        with self._lock:
            self._state.current_task = task_name
            return deepcopy(self._state)

    def set_current_action(self, action_name: str | None) -> RuntimeState:
        with self._lock:
            self._state.current_action = action_name
            return deepcopy(self._state)

    def set_screen_state(self, screen_state: str | None) -> RuntimeState:
        with self._lock:
            self._state.screen_state = screen_state
            return deepcopy(self._state)

    def set_last_error(self, error_message: str | None) -> RuntimeState:
        with self._lock:
            self._state.last_error = error_message
            return deepcopy(self._state)

    def set_selected_tasks(self, tasks: List[str]) -> RuntimeState:
        with self._lock:
            self._state.selected_tasks = list(tasks)
            return deepcopy(self._state)

    def set_cooldown(self, key: str, timestamp: float) -> RuntimeState:
        with self._lock:
            self._state.cooldowns[key] = timestamp
            return deepcopy(self._state)

    def remove_cooldown(self, key: str) -> RuntimeState:
        with self._lock:
            self._state.cooldowns.pop(key, None)
            return deepcopy(self._state)

    def clear_cooldowns(self) -> RuntimeState:
        with self._lock:
            self._state.cooldowns.clear()
            return deepcopy(self._state)

    def set_fail_streak(self, key: str, value: int) -> RuntimeState:
        with self._lock:
            self._state.fail_streaks[key] = value
            return deepcopy(self._state)

    def increment_fail_streak(self, key: str) -> RuntimeState:
        with self._lock:
            self._state.fail_streaks[key] = self._state.fail_streaks.get(key, 0) + 1
            return deepcopy(self._state)

    def clear_fail_streak(self, key: str) -> RuntimeState:
        with self._lock:
            self._state.fail_streaks.pop(key, None)
            return deepcopy(self._state)

    def clear_all_fail_streaks(self) -> RuntimeState:
        with self._lock:
            self._state.fail_streaks.clear()
            return deepcopy(self._state)

    def set_metadata(self, key: str, value: Any) -> RuntimeState:
        with self._lock:
            self._state.metadata[key] = value
            return deepcopy(self._state)

    def remove_metadata(self, key: str) -> RuntimeState:
        with self._lock:
            self._state.metadata.pop(key, None)
            return deepcopy(self._state)

    def update(self, **kwargs: Any) -> RuntimeState:
        with self._lock:
            for key, value in kwargs.items():
                if not hasattr(self._state, key):
                    raise AttributeError(f"Unknown RuntimeState field: '{key}'")
                setattr(self._state, key, value)

            return deepcopy(self._state)

    def mark_started(
        self,
        selected_tasks: List[str],
        profile_name: str | None = None,
        profile_path: str | None = None,
    ) -> RuntimeState:
        with self._lock:
            self._state.running = True
            self._state.paused = False
            self._state.stopping = False
            self._state.last_error = None
            self._state.selected_tasks = list(selected_tasks)

            if profile_name is not None:
                self._state.profile_name = profile_name

            if profile_path is not None:
                self._state.active_profile_path = profile_path

            return deepcopy(self._state)

    def mark_stopped(self) -> RuntimeState:
        with self._lock:
            self._state.running = False
            self._state.paused = False
            self._state.stopping = False
            self._state.current_task = None
            self._state.current_action = None
            self._state.screen_state = None
            return deepcopy(self._state)
