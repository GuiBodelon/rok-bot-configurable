from __future__ import annotations

from typing import Any, Dict, List

from core.tasks import TaskRegistry
from core.tasks.base import TaskContext

from core.runtime import EventBus, RuntimeEngine, StateStore


class DummyTask:
    id = "dummy"
    display_name = "Dummy Task"

    def config_schema(self) -> Dict[str, Any]:
        return {}

    def calibration_steps(self) -> List[Dict[str, Any]]:
        return []

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        return []

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        return True

    def run(self, ctx: TaskContext) -> bool:
        ctx.emit("dummy.executed", {"task_id": self.id})
        return True


def main() -> None:
    state_store = StateStore()
    event_bus = EventBus()
    task_registry = TaskRegistry()

    task_registry.register(DummyTask())

    profile = {
        "profile_name": "Example Profile",
        "tasks": {
            "dummy": {
                "enabled": True,
            }
        },
    }

    state_store.mark_started(selected_tasks=["dummy"], profile_name="Example Profile")

    engine = RuntimeEngine(
        state_store=state_store,
        event_bus=event_bus,
        task_registry=task_registry,
    )

    results = engine.run_once(profile=profile)
    print(results)


if __name__ == "__main__":
    main()
