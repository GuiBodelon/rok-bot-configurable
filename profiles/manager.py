from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class ProfileValidationError(Exception):
    """Erro lançado quando o profile é inválido."""

    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        message = "Profile inválido:\n- " + "\n- ".join(errors)
        super().__init__(message)


class ProfileManager:
    """Responsável por carregar, salvar e validar profiles."""

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
            raise FileNotFoundError(f"Profile não encontrado: {path}")

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
            return ["O conteúdo do profile deve ser um objeto JSON."]

        self._validate_root(profile_data, errors)
        self._validate_display(profile_data, errors)
        self._validate_runtime(profile_data, errors)
        self._validate_global_regions(profile_data, errors)
        self._validate_tasks(profile_data, errors)

        return errors

    def _validate_root(self, profile_data: Dict[str, Any], errors: List[str]) -> None:
        for key in self.REQUIRED_ROOT_KEYS:
            if key not in profile_data:
                errors.append(f"Campo obrigatório ausente na raiz: '{key}'.")

        schema_version = profile_data.get("schema_version")
        if schema_version is not None and not isinstance(schema_version, int):
            errors.append("O campo 'schema_version' deve ser inteiro.")

        profile_name = profile_data.get("profile_name")
        if profile_name is not None:
            if not isinstance(profile_name, str) or not profile_name.strip():
                errors.append("O campo 'profile_name' deve ser uma string não vazia.")

    def _validate_display(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        display = profile_data.get("display")

        if display is None:
            return

        if not isinstance(display, dict):
            errors.append("O campo 'display' deve ser um objeto.")
            return

        for key in self.REQUIRED_DISPLAY_KEYS:
            if key not in display:
                errors.append(f"Campo obrigatório ausente em 'display': '{key}'.")

        monitor_resolution = display.get("monitor_resolution")
        if monitor_resolution is not None and not isinstance(monitor_resolution, str):
            errors.append("O campo 'display.monitor_resolution' deve ser string.")

        windows_scale = display.get("windows_scale_percent")
        if windows_scale is not None:
            if not isinstance(windows_scale, int):
                errors.append(
                    "O campo 'display.windows_scale_percent' deve ser inteiro."
                )
            elif windows_scale <= 0:
                errors.append(
                    "O campo 'display.windows_scale_percent' deve ser maior que zero."
                )

        game_language = display.get("game_language")
        if game_language is not None:
            if not isinstance(game_language, str) or not game_language.strip():
                errors.append(
                    "O campo 'display.game_language' deve ser uma string não vazia."
                )

        game_window = display.get("game_window")
        if game_window is not None:
            if not isinstance(game_window, dict):
                errors.append("O campo 'display.game_window' deve ser um objeto.")
            else:
                for key in self.REQUIRED_GAME_WINDOW_KEYS:
                    if key not in game_window:
                        errors.append(
                            f"Campo obrigatório ausente em 'display.game_window': '{key}'."
                        )

                for key in self.REQUIRED_GAME_WINDOW_KEYS:
                    value = game_window.get(key)
                    if value is not None and not isinstance(value, int):
                        errors.append(
                            f"O campo 'display.game_window.{key}' deve ser inteiro."
                        )

                width = game_window.get("width")
                height = game_window.get("height")

                if isinstance(width, int) and width <= 0:
                    errors.append(
                        "O campo 'display.game_window.width' deve ser maior que zero."
                    )

                if isinstance(height, int) and height <= 0:
                    errors.append(
                        "O campo 'display.game_window.height' deve ser maior que zero."
                    )

    def _validate_runtime(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        runtime = profile_data.get("runtime")

        if runtime is None:
            return

        if not isinstance(runtime, dict):
            errors.append("O campo 'runtime' deve ser um objeto.")
            return

        for key in self.REQUIRED_RUNTIME_KEYS:
            if key not in runtime:
                errors.append(f"Campo obrigatório ausente em 'runtime': '{key}'.")

        default_confidence = runtime.get("default_confidence")
        if default_confidence is not None:
            if not isinstance(default_confidence, (int, float)):
                errors.append("O campo 'runtime.default_confidence' deve ser numérico.")
            elif not 0 <= float(default_confidence) <= 1:
                errors.append(
                    "O campo 'runtime.default_confidence' deve estar entre 0 e 1."
                )

        click_mode = runtime.get("click_mode")
        if click_mode is not None:
            if not isinstance(click_mode, str):
                errors.append("O campo 'runtime.click_mode' deve ser string.")
            elif click_mode not in self.ALLOWED_CLICK_MODES:
                allowed = ", ".join(sorted(self.ALLOWED_CLICK_MODES))
                errors.append(
                    f"O campo 'runtime.click_mode' deve ser um destes valores: {allowed}."
                )

        capture_screenshot = runtime.get("capture_screenshot_on_fail")
        if capture_screenshot is not None and not isinstance(capture_screenshot, bool):
            errors.append(
                "O campo 'runtime.capture_screenshot_on_fail' deve ser booleano."
            )

    def _validate_global_regions(
        self, profile_data: Dict[str, Any], errors: List[str]
    ) -> None:
        global_regions = profile_data.get("global_regions")

        if global_regions is None:
            return

        if not isinstance(global_regions, dict):
            errors.append("O campo 'global_regions' deve ser um objeto.")
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
            errors.append("O campo 'tasks' deve ser um objeto.")
            return

        for task_name, task_data in tasks.items():
            if not isinstance(task_data, dict):
                errors.append(f"O campo 'tasks.{task_name}' deve ser um objeto.")
                continue

            enabled = task_data.get("enabled")
            if enabled is not None and not isinstance(enabled, bool):
                errors.append(f"O campo 'tasks.{task_name}.enabled' deve ser booleano.")

            regions = task_data.get("regions")
            if regions is not None:
                if not isinstance(regions, dict):
                    errors.append(
                        f"O campo 'tasks.{task_name}.regions' deve ser um objeto."
                    )
                else:
                    for region_name, region_value in regions.items():
                        self._validate_region(
                            value=region_value,
                            field_name=f"tasks.{task_name}.regions.{region_name}",
                            errors=errors,
                        )

            points = task_data.get("points")
            if points is not None:
                if not isinstance(points, dict):
                    errors.append(
                        f"O campo 'tasks.{task_name}.points' deve ser um objeto."
                    )
                else:
                    for point_name, point_value in points.items():
                        self._validate_point(
                            value=point_value,
                            field_name=f"tasks.{task_name}.points.{point_name}",
                            errors=errors,
                        )

            assets = task_data.get("assets")
            if assets is not None and not isinstance(assets, dict):
                errors.append(f"O campo 'tasks.{task_name}.assets' deve ser um objeto.")

            settings = task_data.get("settings")
            if settings is not None and not isinstance(settings, dict):
                errors.append(
                    f"O campo 'tasks.{task_name}.settings' deve ser um objeto."
                )

    def _validate_region(self, value: Any, field_name: str, errors: List[str]) -> None:
        if not isinstance(value, list):
            errors.append(
                f"O campo '{field_name}' deve ser uma lista [x, y, width, height]."
            )
            return

        if len(value) != 4:
            errors.append(f"O campo '{field_name}' deve possuir exatamente 4 valores.")
            return

        if not all(isinstance(item, int) for item in value):
            errors.append(f"O campo '{field_name}' deve conter apenas inteiros.")
            return

        _, _, width, height = value
        if width <= 0 or height <= 0:
            errors.append(
                f"O campo '{field_name}' deve ter width e height maiores que zero."
            )

    def _validate_point(self, value: Any, field_name: str, errors: List[str]) -> None:
        if not isinstance(value, list):
            errors.append(f"O campo '{field_name}' deve ser uma lista [x, y].")
            return

        if len(value) != 2:
            errors.append(f"O campo '{field_name}' deve possuir exatamente 2 valores.")
            return

        if not all(isinstance(item, int) for item in value):
            errors.append(f"O campo '{field_name}' deve conter apenas inteiros.")
