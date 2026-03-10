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
                "btn_buscar": [int, int, int, int],
                "btn_reunir": [int, int, int, int],
                "btn_marchar": [int, int, int, int],
                "sem_unidades": [int, int, int, int],
            },
            "points": {
                "search_open": [int, int],
            },
            "assets": {
                "btn_buscar": str,
                "btn_reunir": str,
                "btn_marchar": str,
                "sem_unidades": str,
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
                "key": "btn_buscar",
                "label": "Select the search button region",
            },
            {
                "type": "region",
                "key": "btn_reunir",
                "label": "Select the gather button region",
            },
            {
                "type": "region",
                "key": "btn_marchar",
                "label": "Select the march button region",
            },
            {
                "type": "region",
                "key": "sem_unidades",
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
