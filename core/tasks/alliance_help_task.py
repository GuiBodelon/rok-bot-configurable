from __future__ import annotations

from typing import Any, Dict, List

from core.tasks.base import TaskContext


class AllianceHelpTask:
    id = "alliance_help"
    display_name = "Alliance Help"

    def config_schema(self) -> Dict[str, Any]:
        return {
            "enabled": bool,
            "regions": {
                "help_button": [int, int, int, int],
            },
            "points": {},
            "assets": {},
            "settings": {},
        }

    def calibration_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "region",
                "key": "help_button",
                "label": "Select the alliance help button region",
            },
        ]

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        task_config = profile.get("tasks", {}).get(self.id)

        if not isinstance(task_config, dict):
            return ["Task 'alliance_help' configuration is missing."]

        if "regions" not in task_config or not isinstance(task_config["regions"], dict):
            errors.append("Task 'alliance_help' must define a valid 'regions' object.")

        return errors

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        task_config = profile.get("tasks", {}).get(self.id, {})
        return bool(task_config.get("enabled", False))

    def run(self, ctx: TaskContext) -> bool:
        ctx.emit(
            "task.alliance_help.placeholder_executed",
            {
                "task_id": self.id,
                "message": "Alliance help task stub executed.",
            },
        )
        return True
