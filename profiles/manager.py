from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class ProfileValidationError(Exception):
    """Raised when the profile is invalid."""

    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        message = "Invalid profile:\n- " + "\n- ".join(errors)
        super().__init__(message)


class ProfileManager:
    """Responsible for loading, saving, and validating profiles."""

    REQUIRED_ROOT_KEYS = [
        "schema_version",
        "profile_name",
        "display",
        "runtime",
        "global_regions",
        "tasks",
    ]

    REQUIRED_DISPLAY_KEYS = [
        "monitor_resolution",
        "windows_scale_percent",
        "game_language",
        "game_window",
    ]

    REQUIRED_GAME_WINDOW_KEYS = [
        "x",
        "y",
        "width",
        "height",
    ]

    REQUIRED_RUNTIME_KEYS = [
        "default_confidence",
        "click_mode",
        "capture_screenshot_on_fail",
    ]

    ALLOWED_CLICK_MODES = {
        "humanized",
        "fast",
        "precise",
    }

    def load(self, file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.validate(data)
        return data

    def save(self, file_path: str | Path, profile_data: Dict[str, Any]) -> None:
        self.validate(profile_data)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(profile_data, file, indent=2, ensure_ascii=False)

    def validate(self, profile_data: Dict[str, Any]) -> None:
        errors = self.get_validation_errors(profile_data)

        if errors:
            raise ProfileValidationError(errors)

    def get_validation_errors(self, profile_data: Dict[str, Any]) -> List[str]:
        errors: List[str] = []

        if not isinstance(profile_data, dict):
            return ["Profile content must be a JSON object."]

        self._validate_root(profile_data, errors)
        self._validate_display(profile_data, errors)
        self._validate_runtime(profile_data, errors)
        self._validate_global_regions(profile_data, errors)
        self._validate_tasks(profile_data, errors)

        return errors

    def _validate_root(self, profile_data: Dict[str, Any], errors: List[str]) -> None:
        for key in self.REQUIRED_ROOT_KEYS:
            if key not in profile_data:
                errors.append(f"Missing required root field: '{key}'.")

        schema_version = profile_data.get("schema_version")
        if schema_version is not None and not isinstance(schema_version, int):
            errors.append("Field 'schema_version' must be an integer.")

        profile_name = profile_data.get("profile_name")
        if profile_name is not None:
            if not isinstance(profile_name, str) or not profile_name.strip():
                errors.append("Field 'profile_name' must be a non-empty string.")

    def _validate_display(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        display = profile_data.get("display")

        if display is None:
            return

        if not isinstance(display, dict):
            errors.append("Field 'display' must be an object.")
            return

        for key in self.REQUIRED_DISPLAY_KEYS:
            if key not in display:
                errors.append(f"Missing required field in 'display': '{key}'.")

        monitor_resolution = display.get("monitor_resolution")
        if monitor_resolution is not None and not isinstance(monitor_resolution, str):
            errors.append("Field 'display.monitor_resolution' must be a string.")

        windows_scale = display.get("windows_scale_percent")
        if windows_scale is not None:
            if not isinstance(windows_scale, int):
                errors.append(
                    "Field 'display.windows_scale_percent' must be an integer."
                )
            elif windows_scale <= 0:
                errors.append(
                    "Field 'display.windows_scale_percent' must be greater than zero."
                )

        game_language = display.get("game_language")
        if game_language is not None:
            if not isinstance(game_language, str) or not game_language.strip():
                errors.append(
                    "Field 'display.game_language' must be a non-empty string."
                )

        game_window = display.get("game_window")
        if game_window is not None:
            if not isinstance(game_window, dict):
                errors.append("Field 'display.game_window' must be an object.")
            else:
                for key in self.REQUIRED_GAME_WINDOW_KEYS:
                    if key not in game_window:
                        errors.append(
                            f"Missing required field in 'display.game_window': '{key}'."
                        )

                for key in self.REQUIRED_GAME_WINDOW_KEYS:
                    value = game_window.get(key)
                    if value is not None and not isinstance(value, int):
                        errors.append(
                            f"Field 'display.game_window.{key}' must be an integer."
                        )

                width = game_window.get("width")
                height = game_window.get("height")

                if isinstance(width, int) and width <= 0:
                    errors.append(
                        "Field 'display.game_window.width' must be greater than zero."
                    )

                if isinstance(height, int) and height <= 0:
                    errors.append(
                        "Field 'display.game_window.height' must be greater than zero."
                    )

    def _validate_runtime(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        runtime = profile_data.get("runtime")

        if runtime is None:
            return

        if not isinstance(runtime, dict):
            errors.append("Field 'runtime' must be an object.")
            return

        for key in self.REQUIRED_RUNTIME_KEYS:
            if key not in runtime:
                errors.append(f"Missing required field in 'runtime': '{key}'.")

        default_confidence = runtime.get("default_confidence")
        if default_confidence is not None:
            if not isinstance(default_confidence, (int, float)):
                errors.append("Field 'runtime.default_confidence' must be numeric.")
            elif not 0 <= float(default_confidence) <= 1:
                errors.append(
                    "Field 'runtime.default_confidence' must be between 0 and 1."
                )

        click_mode = runtime.get("click_mode")
        if click_mode is not None:
            if not isinstance(click_mode, str):
                errors.append("Field 'runtime.click_mode' must be a string.")
            elif click_mode not in self.ALLOWED_CLICK_MODES:
                allowed = ", ".join(sorted(self.ALLOWED_CLICK_MODES))
                errors.append(f"Field 'runtime.click_mode' must be one of: {allowed}.")

        capture_screenshot = runtime.get("capture_screenshot_on_fail")
        if capture_screenshot is not None and not isinstance(capture_screenshot, bool):
            errors.append(
                "Field 'runtime.capture_screenshot_on_fail' must be a boolean."
            )

    def _validate_global_regions(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        global_regions = profile_data.get("global_regions")

        if global_regions is None:
            return

        if not isinstance(global_regions, dict):
            errors.append("Field 'global_regions' must be an object.")
            return

        for region_name, region_value in global_regions.items():
            self._validate_region(
                value=region_value,
                field_name=f"global_regions.{region_name}",
                errors=errors,
            )

    def _validate_tasks(self, profile_data: Dict[str, Any], errors: List[str]) -> None:
        tasks = profile_data.get("tasks")

        if tasks is None:
            return

        if not isinstance(tasks, dict):
            errors.append("Field 'tasks' must be an object.")
            return

        for task_name, task_config in tasks.items():
            if not isinstance(task_name, str) or not task_name.strip():
                errors.append("Task names must be non-empty strings.")
                continue

            if not isinstance(task_config, dict):
                errors.append(f"Field 'tasks.{task_name}' must be an object.")
