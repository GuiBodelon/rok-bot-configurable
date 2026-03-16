from __future__ import annotations

from pathlib import Path

from core.controller import BotController
from core.tasks import AllianceHelpTask, FarmTask, ScoutTask, TrainTask


class DummyVisionService:
    def region_exists(self, region):
        return bool(region)


class DummyInputService:
    def click_region(self, region, click_mode="humanized"):
        return bool(region) and isinstance(click_mode, str)


def main() -> None:
    controller = BotController()

    controller.runtime_engine.vision_service = DummyVisionService()
    controller.runtime_engine.input_service = DummyInputService()

    controller.register_task(FarmTask())
    controller.register_task(ScoutTask())
    controller.register_task(TrainTask())
    controller.register_task(AllianceHelpTask())

    profile_path = Path("profiles/storage/example.json")
    controller.load_profile(profile_path)

    selected_tasks = controller.start_from_profile()
    print("Selected tasks:", selected_tasks)

    results = controller.run_cycle()
    print("Cycle results:", results)

    controller.stop()
    print("Final state:", controller.get_runtime_state())


if __name__ == "__main__":
    main()
