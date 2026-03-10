from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from core.tasks.base import TaskContext

from core.controller import BotController


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
    controller = BotController()
    controller.register_task(DummyTask())

    profile_path = Path("profiles/storage/example.profile.json")
    controller.load_profile(profile_path)

    controller.start(selected_tasks=["dummy"])
    results = controller.run_cycle()
    controller.stop()

    print(results)


if __name__ == "__main__":
    main()
