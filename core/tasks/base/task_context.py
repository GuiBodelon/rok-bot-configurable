from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from core.runtime.event_bus import EventBus
from core.runtime.state_store import StateStore


class TaskContextError(Exception):
    """Raised when a task context dependency is missing or invalid."""


@dataclass(slots=True)
class TaskContext:
    """
    Provides the runtime dependencies and helpers required by a task.

    This object is intentionally lightweight and framework-agnostic.
    It gives tasks access to the current profile, runtime state, event bus,
    and optional low-level services that will be connected progressively.
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

    def get_task_regions(self, task_id: str) -> Dict[str, Any]:
        task_config = self.get_task_config(task_id)
        regions = task_config.get("regions", {})
        return regions if isinstance(regions, dict) else {}

    def get_task_points(self, task_id: str) -> Dict[str, Any]:
        task_config = self.get_task_config(task_id)
        points = task_config.get("points", {})
        return points if isinstance(points, dict) else {}

    def get_task_assets(self, task_id: str) -> Dict[str, Any]:
        task_config = self.get_task_config(task_id)
        assets = task_config.get("assets", {})
        return assets if isinstance(assets, dict) else {}

    def get_task_settings(self, task_id: str) -> Dict[str, Any]:
        task_config = self.get_task_config(task_id)
        settings = task_config.get("settings", {})
        return settings if isinstance(settings, dict) else {}

    def get_region(self, task_id: str, region_key: str) -> Optional[Any]:
        return self.get_task_regions(task_id).get(region_key)

    def get_point(self, task_id: str, point_key: str) -> Optional[Any]:
        return self.get_task_points(task_id).get(point_key)

    def get_asset(self, task_id: str, asset_key: str) -> Optional[Any]:
        return self.get_task_assets(task_id).get(asset_key)

    def get_setting(
        self, task_id: str, setting_key: str, default: Optional[Any] = None
    ) -> Any:
        return self.get_task_settings(task_id).get(setting_key, default)

    def require_service(self, service_name: str) -> Any:
        service = getattr(self, service_name, None)
        if service is None:
            raise TaskContextError(
                f"Required service '{service_name}' is not available in task context."
            )
        return service

    def emit(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Emits a runtime event through the shared event bus.
        """
        self.event_bus.emit(event_name, payload or {})

    def set_current_action(self, action_name: Optional[str]) -> None:
        self.state_store.set_current_action(action_name)
        self.emit(
            "runtime.current_action_changed",
            {
                "current_action": action_name,
            },
        )

    def set_screen_state(self, screen_state: Optional[str]) -> None:
        self.state_store.set_screen_state(screen_state)
        self.emit(
            "runtime.screen_state_changed",
            {
                "screen_state": screen_state,
            },
        )

    def set_last_error(self, error_message: Optional[str]) -> None:
        self.state_store.set_last_error(error_message)
        self.emit(
            "runtime.error_updated",
            {
                "last_error": error_message,
            },
        )

    def get_runtime_state(self) -> Dict[str, Any]:
        """
        Returns the current runtime state as a dictionary snapshot.
        """
        return self.state_store.to_dict()
