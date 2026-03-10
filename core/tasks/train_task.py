from __future__ import annotations

from typing import Any, Dict, List

from core.tasks.base import TaskContext


class TrainTask:
    id = "train"
    display_name = "Train"

    def config_schema(self) -> Dict[str, Any]:
        return {
            "enabled": bool,
            "regions": {
                "building_trigger": [int, int, int, int],
                "train_button": [int, int, int, int],
                "confirm_button": [int, int, int, int],
            },
            "points": {},
            "assets": {},
            "settings": {
                "troop_type": str,
            },
        }

    def calibration_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "region",
                "key": "building_trigger",
                "label": "Select the training building trigger region",
            },
            {
                "type": "region",
                "key": "train_button",
                "label": "Select the train button region",
            },
            {
                "type": "region",
                "key": "confirm_button",
                "label": "Select the confirm train button region",
            },
        ]

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        task_config = profile.get("tasks", {}).get(self.id)

        if not isinstance(task_config, dict):
            return ["Task 'train' configuration is missing."]

        for key in ("regions", "settings"):
            if key not in task_config or not isinstance(task_config[key], dict):
                errors.append(f"Task 'train' must define a valid '{key}' object.")

        return errors

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        task_config = profile.get("tasks", {}).get(self.id, {})
        return bool(task_config.get("enabled", False))

    def run(self, ctx: TaskContext) -> bool:
        ctx.emit(
            "task.train.placeholder_executed",
            {
                "task_id": self.id,
                "message": "Train task stub executed.",
            },
        )
        return True
