from __future__ import annotations

from typing import Any, Dict, List

from core.tasks.base import TaskContext


class FarmTask:
    id = "farm"
    display_name = "Farm"

    def config_schema(self) -> Dict[str, Any]:
        return {
            "enabled": bool,
            "regions": {
                "search_button": [int, int, int, int],
                "gather_button": [int, int, int, int],
                "march_button": [int, int, int, int],
                "no_units": [int, int, int, int],
            },
            "points": {
                "search_open": [int, int],
            },
            "assets": {
                "search_button": str,
                "gather_button": str,
                "march_button": str,
                "no_units": str,
            },
            "settings": {
                "resource_type": str,
                "resource_level": int,
            },
        }

    def calibration_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "region",
                "key": "search_button",
                "label": "Select the search button region",
            },
            {
                "type": "region",
                "key": "gather_button",
                "label": "Select the gather button region",
            },
            {
                "type": "region",
                "key": "march_button",
                "label": "Select the march button region",
            },
            {
                "type": "region",
                "key": "no_units",
                "label": "Select the no-units warning region",
            },
            {
                "type": "point",
                "key": "search_open",
                "label": "Select the search panel open point",
            },
        ]

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        task_config = profile.get("tasks", {}).get(self.id)

        if not isinstance(task_config, dict):
            return ["Task 'farm' configuration is missing."]

        for key in ("regions", "points", "assets", "settings"):
            if key not in task_config or not isinstance(task_config[key], dict):
                errors.append(f"Task 'farm' must define a valid '{key}' object.")

        return errors

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        task_config = profile.get("tasks", {}).get(self.id, {})
        return bool(task_config.get("enabled", False))

    def run(self, ctx: TaskContext) -> bool:
        ctx.emit(
            "task.farm.placeholder_executed",
            {
                "task_id": self.id,
                "message": "Farm task stub executed.",
            },
        )
        return True
