from __future__ import annotations

from typing import Any, Dict, Optional

from core.runtime.event_bus import EventBus
from core.runtime.state_store import StateStore
from core.tasks.base.task_context import TaskContext
from core.tasks.registry import TaskRegistry, TaskRegistryError


class RuntimeEngineError(Exception):
    """Base error for runtime engine failures."""


class RuntimeEngine:
    """
    Coordinates task execution using the current runtime state.

    Responsibilities:
    - resolve selected tasks from the registry
    - build task execution context
    - execute tasks sequentially
    - update runtime state during execution
    - emit lifecycle and failure events
    """

    def __init__(
        self,
        state_store: StateStore,
        event_bus: EventBus,
        task_registry: TaskRegistry,
        vision_service: Optional[Any] = None,
        input_service: Optional[Any] = None,
        guard_service: Optional[Any] = None,
        cooldown_service: Optional[Any] = None,
    ) -> None:
        self.state_store = state_store
        self.event_bus = event_bus
        self.task_registry = task_registry
        self.vision_service = vision_service
        self.input_service = input_service
        self.guard_service = guard_service
        self.cooldown_service = cooldown_service

    def run_once(self, profile: Dict[str, Any]) -> Dict[str, bool]:
        """
        Executes a single pass across all selected tasks.

        Returns:
            Dict[str, bool]: A mapping of task ID to execution result.
        """
        state = self.state_store.get_state()

        if not state.running:
            raise RuntimeEngineError("Runtime is not marked as running.")

        if state.paused:
            self.event_bus.emit("runtime.cycle_skipped", {"reason": "paused"})
            return {}

        if state.stopping:
            self.event_bus.emit("runtime.cycle_skipped", {"reason": "stopping"})
            return {}

        selected_tasks = list(state.selected_tasks)
        if not selected_tasks:
            self.event_bus.emit(
                "runtime.cycle_skipped", {"reason": "no_selected_tasks"}
            )
            return {}

        results: Dict[str, bool] = {}

        self.event_bus.emit(
            "runtime.cycle_started",
            {
                "selected_tasks": selected_tasks,
            },
        )

        for task_id in selected_tasks:
            state = self.state_store.get_state()

            if not state.running or state.stopping:
                self.event_bus.emit(
                    "runtime.cycle_interrupted",
                    {
                        "task_id": task_id,
                        "reason": "runtime_stopped",
                    },
                )
                break

            if state.paused:
                self.event_bus.emit(
                    "runtime.cycle_interrupted",
                    {
                        "task_id": task_id,
                        "reason": "runtime_paused",
                    },
                )
                break

            results[task_id] = self._run_task(task_id=task_id, profile=profile)

        self.state_store.set_current_task(None)
        self.state_store.set_current_action(None)

        self.event_bus.emit(
            "runtime.cycle_finished",
            {
                "results": results,
            },
        )

        return results

    def _run_task(self, task_id: str, profile: Dict[str, Any]) -> bool:
        try:
            task = self.task_registry.get(task_id)
        except TaskRegistryError as exc:
            self.state_store.set_last_error(str(exc))
            self.state_store.increment_fail_streak(task_id)

            self.event_bus.emit(
                "task.failed",
                {
                    "task_id": task_id,
                    "reason": "task_not_registered",
                    "error": str(exc),
                },
            )
            return False

        validation_errors = task.validate_config(profile)
        if validation_errors:
            self.state_store.set_last_error("; ".join(validation_errors))
            self.state_store.increment_fail_streak(task_id)

            self.event_bus.emit(
                "task.validation_failed",
                {
                    "task_id": task_id,
                    "errors": validation_errors,
                },
            )
            return False

        self.state_store.set_current_task(task_id)
        self.state_store.set_current_action("running")
        self.state_store.set_last_error(None)

        self.event_bus.emit(
            "task.started",
            {
                "task_id": task.id,
                "display_name": task.display_name,
            },
        )

        ctx = self._build_task_context(profile=profile, task_id=task_id)

        try:
            success = task.run(ctx)
        except Exception as exc:
            self.state_store.set_last_error(str(exc))
            self.state_store.increment_fail_streak(task_id)

            self.event_bus.emit(
                "task.failed",
                {
                    "task_id": task.id,
                    "display_name": task.display_name,
                    "reason": "unhandled_exception",
                    "error": str(exc),
                },
            )
            return False

        if success:
            self.state_store.clear_fail_streak(task_id)
            self.state_store.set_current_action("completed")

            self.event_bus.emit(
                "task.completed",
                {
                    "task_id": task.id,
                    "display_name": task.display_name,
                    "success": True,
                },
            )
            return True

        self.state_store.increment_fail_streak(task_id)
        self.state_store.set_current_action("failed")

        self.event_bus.emit(
            "task.failed",
            {
                "task_id": task.id,
                "display_name": task.display_name,
                "reason": "task_returned_false",
            },
        )
        return False

    def _build_task_context(self, profile: Dict[str, Any], task_id: str) -> TaskContext:
        return TaskContext(
            profile=profile,
            state_store=self.state_store,
            event_bus=self.event_bus,
            vision_service=self.vision_service,
            input_service=self.input_service,
            guard_service=self.guard_service,
            cooldown_service=self.cooldown_service,
            metadata={
                "task_id": task_id,
            },
        )
