from __future__ import annotations

from typing import Any, Dict, List

from core.tasks.base import TaskContext


class ScoutTask:
    id = "scout"
    display_name = "Scout"

    def config_schema(self) -> Dict[str, Any]:
        return {
            "enabled": bool,
            "regions": {
                "gatilho_scout": [int, int, int, int],
                "btn_abrir_menu": [int, int, int, int],
                "btn_explorar_painel": [int, int, int, int],
                "btn_explorar_mapa": [int, int, int, int],
                "btn_enviar": [int, int, int, int],
            },
            "points": {},
            "assets": {},
            "settings": {},
        }

    def calibration_steps(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "region",
                "key": "gatilho_scout",
                "label": "Select the scout trigger region",
            },
            {
                "type": "region",
                "key": "btn_abrir_menu",
                "label": "Select the scout menu button region",
            },
            {
                "type": "region",
                "key": "btn_explorar_painel",
                "label": "Select the panel explore button region",
            },
            {
                "type": "region",
                "key": "btn_explorar_mapa",
                "label": "Select the map explore button region",
            },
            {
                "type": "region",
                "key": "btn_enviar",
                "label": "Select the send button region",
            },
        ]

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        task_config = profile.get("tasks", {}).get(self.id)

        if not isinstance(task_config, dict):
            return ["Task 'scout' configuration is missing."]

        if "regions" not in task_config or not isinstance(task_config["regions"], dict):
            errors.append("Task 'scout' must define a valid 'regions' object.")

        return errors

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        task_config = profile.get("tasks", {}).get(self.id, {})
        return bool(task_config.get("enabled", False))

    def run(self, ctx: TaskContext) -> bool:
        ctx.emit(
            "task.scout.placeholder_executed",
            {
                "task_id": self.id,
                "message": "Scout task stub executed.",
            },
        )
        return True
