from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from core.runtime import EventBus, StateStore
from profiles import ProfileManager, ProfileValidationError


class BotControllerError(Exception):
    """Erro base do controller."""


class BotController:
    """
    Camada de orquestração entre UI e runtime.

    Responsabilidades:
    - carregar e validar profile
    - iniciar, pausar, retomar e parar o runtime
    - refletir mudanças no StateStore
    - publicar eventos para observadores externos
    """

    def __init__(
        self,
        profile_manager: Optional[ProfileManager] = None,
        state_store: Optional[StateStore] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.profile_manager = profile_manager or ProfileManager()
        self.state_store = state_store or StateStore()
        self.event_bus = event_bus or EventBus()

        self._active_profile: Optional[Dict[str, Any]] = None
        self._active_profile_path: Optional[str] = None

    @property
    def active_profile(self) -> Optional[Dict[str, Any]]:
        if self._active_profile is None:
            return None
        return dict(self._active_profile)

    @property
    def active_profile_path(self) -> Optional[str]:
        return self._active_profile_path

    def load_profile(self, profile_path: str | Path) -> Dict[str, Any]:
        path = Path(profile_path)

        try:
            profile = self.profile_manager.load(path)
        except FileNotFoundError as exc:
            self._publish_error("profile.load_failed", str(exc))
            raise BotControllerError(str(exc)) from exc
        except ProfileValidationError as exc:
            self._publish_error(
                "profile.validation_failed", str(exc), errors=exc.errors
            )
            raise BotControllerError(str(exc)) from exc
        except Exception as exc:
            self._publish_error(
                "profile.load_failed", f"Falha inesperada ao carregar profile: {exc}"
            )
            raise BotControllerError(
                f"Falha inesperada ao carregar profile: {exc}"
            ) from exc

        self._active_profile = profile
        self._active_profile_path = str(path)

        profile_name = profile.get("profile_name", "Sem nome")
        self.state_store.set_profile(profile_name=profile_name, profile_path=str(path))
        self.state_store.set_last_error(None)

        self.event_bus.emit(
            "profile.loaded",
            {
                "profile_name": profile_name,
                "profile_path": str(path),
                "schema_version": profile.get("schema_version"),
            },
        )

        return profile

    def reload_profile(self) -> Dict[str, Any]:
        if not self._active_profile_path:
            raise BotControllerError("Nenhum profile ativo para recarregar.")

        return self.load_profile(self._active_profile_path)

    def unload_profile(self) -> None:
        profile_name = self.state_store.get_state().profile_name

        self._active_profile = None
        self._active_profile_path = None
        self.state_store.reset()

        self.event_bus.emit(
            "profile.unloaded",
            {
                "previous_profile_name": profile_name,
            },
        )

    def validate_before_run(self, selected_tasks: List[str]) -> List[str]:
        errors: List[str] = []

        if self._active_profile is None:
            errors.append("Nenhum profile foi carregado.")

        if not selected_tasks:
            errors.append("Nenhuma task foi selecionada para execução.")

        if self._active_profile is not None:
            profile_tasks = self._active_profile.get("tasks", {})

            for task_name in selected_tasks:
                task_data = profile_tasks.get(task_name)

                if task_data is None:
                    errors.append(f"A task '{task_name}' não existe no profile.")
                    continue

                enabled = task_data.get("enabled")
                if enabled is False:
                    errors.append(f"A task '{task_name}' está desabilitada no profile.")

        if errors:
            self.state_store.set_last_error("; ".join(errors))
            self.event_bus.emit(
                "runtime.validation_failed",
                {
                    "errors": errors,
                    "selected_tasks": selected_tasks,
                },
            )
        else:
            self.state_store.set_last_error(None)
            self.event_bus.emit(
                "runtime.validation_succeeded",
                {
                    "selected_tasks": selected_tasks,
                },
            )

        return errors

    def start(self, selected_tasks: List[str]) -> None:
        state = self.state_store.get_state()

        if state.running:
            raise BotControllerError("O runtime já está em execução.")

        errors = self.validate_before_run(selected_tasks)
        if errors:
            raise BotControllerError("Falha na validação pré-execução.")

        profile_name = (
            self._active_profile.get("profile_name") if self._active_profile else None
        )
        profile_path = self._active_profile_path

        self.state_store.mark_started(
            selected_tasks=selected_tasks,
            profile_name=profile_name,
            profile_path=profile_path,
        )
        self.state_store.set_current_task(None)
        self.state_store.set_current_action(None)
        self.state_store.set_screen_state(None)

        self.event_bus.emit(
            "runtime.started",
            {
                "profile_name": profile_name,
                "profile_path": profile_path,
                "selected_tasks": selected_tasks,
            },
        )

    def pause(self) -> None:
        state = self.state_store.get_state()

        if not state.running:
            raise BotControllerError(
                "Não é possível pausar: o runtime não está em execução."
            )

        if state.paused:
            raise BotControllerError("O runtime já está pausado.")

        self.state_store.set_paused(True)

        self.event_bus.emit(
            "runtime.paused",
            {
                "current_task": state.current_task,
                "current_action": state.current_action,
            },
        )

    def resume(self) -> None:
        state = self.state_store.get_state()

        if not state.running:
            raise BotControllerError(
                "Não é possível retomar: o runtime não está em execução."
            )

        if not state.paused:
            raise BotControllerError(
                "Não é possível retomar: o runtime não está pausado."
            )

        self.state_store.set_paused(False)

        self.event_bus.emit(
            "runtime.resumed",
            {
                "current_task": state.current_task,
                "current_action": state.current_action,
            },
        )

    def stop(self) -> None:
        state = self.state_store.get_state()

        if not state.running and not state.paused:
            raise BotControllerError("Não é possível parar: o runtime não está ativo.")

        self.state_store.mark_stopped()

        self.event_bus.emit(
            "runtime.stopped",
            {
                "previous_task": state.current_task,
                "previous_action": state.current_action,
                "selected_tasks": state.selected_tasks,
            },
        )

    def set_current_task(self, task_name: Optional[str]) -> None:
        self.state_store.set_current_task(task_name)

        self.event_bus.emit(
            "runtime.current_task_changed",
            {
                "current_task": task_name,
            },
        )

    def set_current_action(self, action_name: Optional[str]) -> None:
        self.state_store.set_current_action(action_name)

        self.event_bus.emit(
            "runtime.current_action_changed",
            {
                "current_action": action_name,
            },
        )

    def set_screen_state(self, screen_state: Optional[str]) -> None:
        self.state_store.set_screen_state(screen_state)

        self.event_bus.emit(
            "runtime.screen_state_changed",
            {
                "screen_state": screen_state,
            },
        )

    def set_last_error(self, error_message: Optional[str]) -> None:
        self.state_store.set_last_error(error_message)

        self.event_bus.emit(
            "runtime.error_updated",
            {
                "last_error": error_message,
            },
        )

    def get_runtime_state(self) -> Dict[str, Any]:
        return self.state_store.to_dict()

    def get_selected_tasks_from_profile(self) -> List[str]:
        if self._active_profile is None:
            return []

        tasks = self._active_profile.get("tasks", {})
        return [
            task_name
            for task_name, task_data in tasks.items()
            if task_data.get("enabled") is True
        ]

    def _publish_error(self, event_name: str, message: str, **extra: Any) -> None:
        self.state_store.set_last_error(message)

        payload = {"message": message}
        payload.update(extra)

        self.event_bus.emit(event_name, payload)
