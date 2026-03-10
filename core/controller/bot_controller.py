from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from core.tasks import TaskRegistry
from core.tasks.base import TaskContract

from core.runtime import EventBus, RuntimeEngine, RuntimeEngineError, StateStore
from profiles import ProfileManager, ProfileValidationError


class BotControllerError(Exception):
    """Base controller error."""


class BotController:
    """
    Orchestrates the interaction between profile management, runtime state,
    task registration, and runtime execution.

    Responsibilities:
    - load and validate profiles
    - control runtime lifecycle
    - expose task registration to higher-level layers
    - execute runtime cycles through the runtime engine
    - reflect lifecycle changes in the state store
    - publish events for external observers
    """

    def __init__(
        self,
        profile_manager: Optional[ProfileManager] = None,
        state_store: Optional[StateStore] = None,
        event_bus: Optional[EventBus] = None,
        task_registry: Optional[TaskRegistry] = None,
        runtime_engine: Optional[RuntimeEngine] = None,
    ) -> None:
        self.profile_manager = profile_manager or ProfileManager()
        self.state_store = state_store or StateStore()
        self.event_bus = event_bus or EventBus()
        self.task_registry = task_registry or TaskRegistry()
        self.runtime_engine = runtime_engine or RuntimeEngine(
            state_store=self.state_store,
            event_bus=self.event_bus,
            task_registry=self.task_registry,
        )

        self._active_profile: Optional[Dict[str, Any]] = None
        self._active_profile_path: Optional[str] = None

    @property
    def active_profile(self) -> Optional[Dict[str, Any]]:
        if self._active_profile is None:
            return None
        return dict(self._active_profile)

    @property
    def active_profile_path(self) -> Optional[str]:
        return self._active_profile_path

    def load_profile(self, profile_path: str | Path) -> Dict[str, Any]:
        path = Path(profile_path)

        try:
            profile = self.profile_manager.load(path)
        except FileNotFoundError as exc:
            self._publish_error("profile.load_failed", str(exc))
            raise BotControllerError(str(exc)) from exc
        except ProfileValidationError as exc:
            self._publish_error(
                "profile.validation_failed", str(exc), errors=exc.errors
            )
            raise BotControllerError(str(exc)) from exc
        except Exception as exc:
            self._publish_error(
                "profile.load_failed",
                f"Unexpected failure while loading profile: {exc}",
            )
            raise BotControllerError(
                f"Unexpected failure while loading profile: {exc}"
            ) from exc

        self._active_profile = profile
        self._active_profile_path = str(path)

        profile_name = profile.get("profile_name", "Unnamed Profile")
        self.state_store.set_profile(profile_name=profile_name, profile_path=str(path))
        self.state_store.set_last_error(None)

        self.event_bus.emit(
            "profile.loaded",
            {
                "profile_name": profile_name,
                "profile_path": str(path),
                "schema_version": profile.get("schema_version"),
            },
        )

        return profile

    def reload_profile(self) -> Dict[str, Any]:
        if not self._active_profile_path:
            raise BotControllerError("No active profile is available to reload.")

        return self.load_profile(self._active_profile_path)

    def unload_profile(self) -> None:
        profile_name = self.state_store.get_state().profile_name

        self._active_profile = None
        self._active_profile_path = None
        self.state_store.reset()

        self.event_bus.emit(
            "profile.unloaded",
            {
                "previous_profile_name": profile_name,
            },
        )

    def register_task(self, task: TaskContract) -> None:
        self.task_registry.register(task)

        self.event_bus.emit(
            "task.registered",
            {
                "task_id": task.id,
                "display_name": task.display_name,
            },
        )

    def unregister_task(self, task_id: str) -> None:
        self.task_registry.unregister(task_id)

        self.event_bus.emit(
            "task.unregistered",
            {
                "task_id": task_id,
            },
        )

    def get_registered_tasks(self) -> List[Dict[str, str]]:
        return self.task_registry.describe()

    def validate_before_run(self, selected_tasks: List[str]) -> List[str]:
        errors: List[str] = []

        if self._active_profile is None:
            errors.append("No profile has been loaded.")

        if not selected_tasks:
            errors.append("No tasks were selected for execution.")

        if self._active_profile is not None:
            profile_tasks = self._active_profile.get("tasks", {})

            for task_name in selected_tasks:
                task_data = profile_tasks.get(task_name)

                if task_data is None:
                    errors.append(
                        f"Task '{task_name}' does not exist in the loaded profile."
                    )
                    continue

                enabled = task_data.get("enabled")
                if enabled is False:
                    errors.append(
                        f"Task '{task_name}' is disabled in the loaded profile."
                    )

                if not self.task_registry.has(task_name):
                    errors.append(
                        f"Task '{task_name}' is not registered in the runtime."
                    )

        if errors:
            self.state_store.set_last_error("; ".join(errors))
            self.event_bus.emit(
                "runtime.validation_failed",
                {
                    "errors": errors,
                    "selected_tasks": selected_tasks,
                },
            )
        else:
            self.state_store.set_last_error(None)
            self.event_bus.emit(
                "runtime.validation_succeeded",
                {
                    "selected_tasks": selected_tasks,
                },
            )

        return errors

    def start(self, selected_tasks: List[str]) -> None:
        state = self.state_store.get_state()

        if state.running:
            raise BotControllerError("Runtime is already running.")

        errors = self.validate_before_run(selected_tasks)
        if errors:
            raise BotControllerError("Pre-run validation failed.")

        profile_name = (
            self._active_profile.get("profile_name") if self._active_profile else None
        )
        profile_path = self._active_profile_path

        self.state_store.mark_started(
            selected_tasks=selected_tasks,
            profile_name=profile_name,
            profile_path=profile_path,
        )
        self.state_store.set_current_task(None)
        self.state_store.set_current_action(None)
        self.state_store.set_screen_state(None)

        self.event_bus.emit(
            "runtime.started",
            {
                "profile_name": profile_name,
                "profile_path": profile_path,
                "selected_tasks": selected_tasks,
            },
        )

    def run_cycle(self) -> Dict[str, bool]:
        if self._active_profile is None:
            raise BotControllerError(
                "Cannot run runtime cycle without an active profile."
            )

        try:
            results = self.runtime_engine.run_once(profile=self._active_profile)
        except RuntimeEngineError as exc:
            self._publish_error("runtime.execution_failed", str(exc))
            raise BotControllerError(str(exc)) from exc
        except Exception as exc:
            self._publish_error(
                "runtime.execution_failed",
                f"Unexpected runtime execution failure: {exc}",
            )
            raise BotControllerError(
                f"Unexpected runtime execution failure: {exc}"
            ) from exc

        self.event_bus.emit(
            "runtime.cycle_results_available",
            {
                "results": results,
            },
        )

        return results

    def pause(self) -> None:
        state = self.state_store.get_state()

        if not state.running:
            raise BotControllerError("Cannot pause because runtime is not running.")

        if state.paused:
            raise BotControllerError("Runtime is already paused.")

        self.state_store.set_paused(True)

        self.event_bus.emit(
            "runtime.paused",
            {
                "current_task": state.current_task,
                "current_action": state.current_action,
            },
        )

    def resume(self) -> None:
        state = self.state_store.get_state()

        if not state.running:
            raise BotControllerError("Cannot resume because runtime is not running.")

        if not state.paused:
            raise BotControllerError("Cannot resume because runtime is not paused.")

        self.state_store.set_paused(False)

        self.event_bus.emit(
            "runtime.resumed",
            {
                "current_task": state.current_task,
                "current_action": state.current_action,
            },
        )

    def stop(self) -> None:
        state = self.state_store.get_state()

        if not state.running and not state.paused:
            raise BotControllerError("Cannot stop because runtime is not active.")

        self.state_store.mark_stopped()

        self.event_bus.emit(
            "runtime.stopped",
            {
                "previous_task": state.current_task,
                "previous_action": state.current_action,
                "selected_tasks": state.selected_tasks,
            },
        )

    def set_current_task(self, task_name: Optional[str]) -> None:
        self.state_store.set_current_task(task_name)

        self.event_bus.emit(
            "runtime.current_task_changed",
            {
                "current_task": task_name,
            },
        )

    def set_current_action(self, action_name: Optional[str]) -> None:
        self.state_store.set_current_action(action_name)

        self.event_bus.emit(
            "runtime.current_action_changed",
            {
                "current_action": action_name,
            },
        )

    def set_screen_state(self, screen_state: Optional[str]) -> None:
        self.state_store.set_screen_state(screen_state)

        self.event_bus.emit(
            "runtime.screen_state_changed",
            {
                "screen_state": screen_state,
            },
        )

    def set_last_error(self, error_message: Optional[str]) -> None:
        self.state_store.set_last_error(error_message)

        self.event_bus.emit(
            "runtime.error_updated",
            {
                "last_error": error_message,
            },
        )

    def get_runtime_state(self) -> Dict[str, Any]:
        return self.state_store.to_dict()

    def get_selected_tasks_from_profile(self) -> List[str]:
        if self._active_profile is None:
            return []

        tasks = self._active_profile.get("tasks", {})
        return [
            task_name
            for task_name, task_data in tasks.items()
            if task_data.get("enabled") is True
        ]

    def _publish_error(self, event_name: str, message: str, **extra: Any) -> None:
        self.state_store.set_last_error(message)

        payload = {"message": message}
        payload.update(extra)

        self.event_bus.emit(event_name, payload)
