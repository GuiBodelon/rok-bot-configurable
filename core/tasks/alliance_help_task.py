from __future__ import annotations

from typing import Any, Dict, List, Optional

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
            "assets": {
                "help_button": str,
            },
            "settings": {
                "confidence": float,
                "click_mode": str,
            },
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

        regions = task_config.get("regions")
        if not isinstance(regions, dict):
            errors.append("Task 'alliance_help' must define a valid 'regions' object.")
            return errors

        help_button_region = regions.get("help_button")
        if help_button_region is None:
            errors.append("Task 'alliance_help' must define 'regions.help_button'.")
        elif not self._is_valid_region(help_button_region):
            errors.append(
                "Task 'alliance_help' field 'regions.help_button' must be a valid region [x, y, width, height]."
            )

        assets = task_config.get("assets")
        if assets is not None and not isinstance(assets, dict):
            errors.append("Task 'alliance_help' field 'assets' must be an object.")

        settings = task_config.get("settings")
        if settings is not None and not isinstance(settings, dict):
            errors.append("Task 'alliance_help' field 'settings' must be an object.")

        return errors

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        task_config = profile.get("tasks", {}).get(self.id, {})
        return bool(task_config.get("enabled", False))

    def run(self, ctx: TaskContext) -> bool:
        ctx.set_current_action("locating_help_button")

        task_config = ctx.get_task_config(self.id)
        regions = task_config.get("regions", {})
        assets = task_config.get("assets", {})
        settings = task_config.get("settings", {})

        help_button_region = regions.get("help_button")
        help_button_asset = assets.get("help_button")
        confidence = float(settings.get("confidence", 0.85))
        click_mode = str(settings.get("click_mode", "humanized"))

        vision_service = ctx.require_service("vision_service")
        input_service = ctx.require_service("input_service")

        ctx.emit(
            "task.alliance_help.search_started",
            {
                "task_id": self.id,
                "region_key": "help_button",
                "confidence": confidence,
                "click_mode": click_mode,
            },
        )

        detection = self._locate_help_button(
            vision_service=vision_service,
            region=help_button_region,
            asset_path=help_button_asset,
            confidence=confidence,
        )

        if detection is None:
            message = "Alliance help button was not detected."
            ctx.set_last_error(message)
            ctx.emit(
                "task.alliance_help.not_found",
                {
                    "task_id": self.id,
                    "region_key": "help_button",
                },
            )
            return False

        ctx.set_current_action("clicking_help_button")

        clicked = self._click_detected_target(
            input_service=input_service,
            detection=detection,
            region=help_button_region,
            click_mode=click_mode,
        )

        if not clicked:
            message = "Alliance help button was detected but could not be clicked."
            ctx.set_last_error(message)
            ctx.emit(
                "task.alliance_help.click_failed",
                {
                    "task_id": self.id,
                    "region_key": "help_button",
                    "click_mode": click_mode,
                },
            )
            return False

        ctx.set_last_error(None)
        ctx.emit(
            "task.alliance_help.completed",
            {
                "task_id": self.id,
                "region_key": "help_button",
                "click_mode": click_mode,
            },
        )
        return True

    def _locate_help_button(
        self,
        vision_service: Any,
        region: Any,
        asset_path: Optional[str],
        confidence: float,
    ) -> Optional[Any]:
        """
        Adapter-friendly lookup strategy.

        Supported vision service styles:
        - locate(asset_path=..., region=..., confidence=...)
        - locate_in_region(asset_path=..., region=..., confidence=...)
        - find(asset_path=..., region=..., confidence=...)
        - detect(asset_path=..., region=..., confidence=...)
        - region_exists(region=...) as fallback when no asset is available
        """
        if asset_path:
            for method_name in ("locate", "locate_in_region", "find", "detect"):
                method = getattr(vision_service, method_name, None)
                if callable(method):
                    return method(
                        asset_path=asset_path,
                        region=region,
                        confidence=confidence,
                    )

        region_exists = getattr(vision_service, "region_exists", None)
        if callable(region_exists):
            exists = region_exists(region=region)
            return {"region": region} if exists else None

        return None

    def _click_detected_target(
        self,
        input_service: Any,
        detection: Any,
        region: Any,
        click_mode: str,
    ) -> bool:
        """
        Adapter-friendly click strategy.

        Supported input service styles:
        - click_target(detection=..., click_mode=...)
        - click_region(region=..., click_mode=...)
        - click(x=..., y=..., mode=...)
        """
        click_target = getattr(input_service, "click_target", None)
        if callable(click_target):
            return bool(
                click_target(
                    detection=detection,
                    click_mode=click_mode,
                )
            )

        click_region = getattr(input_service, "click_region", None)
        if callable(click_region):
            target_region = (
                detection.get("region") if isinstance(detection, dict) else None
            )
            if target_region is None:
                target_region = region
            return bool(
                click_region(
                    region=target_region,
                    click_mode=click_mode,
                )
            )

        click = getattr(input_service, "click", None)
        if callable(click):
            point = self._extract_click_point(detection, region)
            if point is None:
                return False

            x, y = point
            return bool(click(x=x, y=y, mode=click_mode))

        return False

    def _extract_click_point(
        self, detection: Any, fallback_region: Any
    ) -> Optional[tuple[int, int]]:
        if isinstance(detection, dict):
            center = detection.get("center")
            if (
                isinstance(center, (list, tuple))
                and len(center) == 2
                and all(isinstance(v, int) for v in center)
            ):
                return center[0], center[1]

            region = detection.get("region")
            if self._is_valid_region(region):
                x, y, width, height = region
                return x + (width // 2), y + (height // 2)

        if self._is_valid_region(fallback_region):
            x, y, width, height = fallback_region
            return x + (width // 2), y + (height // 2)

        return None

    def _is_valid_region(self, value: Any) -> bool:
        return (
            isinstance(value, list)
            and len(value) == 4
            and all(isinstance(item, int) for item in value)
            and value[2] > 0
            and value[3] > 0
        )
