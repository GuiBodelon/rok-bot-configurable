from __future__ import annotations

from core.controller import BotController
from core.tasks import AllianceHelpTask, FarmTask, ScoutTask, TrainTask


def main() -> None:
    controller = BotController()

    controller.register_task(FarmTask())
    controller.register_task(ScoutTask())
    controller.register_task(TrainTask())
    controller.register_task(AllianceHelpTask())

    print(controller.get_registered_tasks())


if __name__ == "__main__":
    main()
