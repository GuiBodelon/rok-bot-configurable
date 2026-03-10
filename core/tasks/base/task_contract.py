from __future__ import annotations

from typing import Any, Dict, List, Protocol, runtime_checkable

from .task_context import TaskContext


@runtime_checkable
class TaskContract(Protocol):
    """
    Defines the minimum contract that every task must implement.

    A task is an operational unit of the bot, such as farming, scouting,
    training, alliance help, or future automation flows.
    """

    id: str
    display_name: str

    def config_schema(self) -> Dict[str, Any]:
        """
        Returns the configuration schema expected by this task.

        This schema describes the fields that must exist under the task
        configuration inside a profile.
        """
        ...

    def calibration_steps(self) -> List[Dict[str, Any]]:
        """
        Returns the calibration steps required by this task.

        These steps will later be consumed by the onboarding/calibration
        wizard in the desktop application.
        """
        ...

    def validate_config(self, profile: Dict[str, Any]) -> List[str]:
        """
        Validates whether the profile contains the minimum configuration
        required for this task to run.

        Returns a list of validation errors. An empty list means success.
        """
        ...

    def is_enabled(self, profile: Dict[str, Any]) -> bool:
        """
        Returns whether the task is enabled in the provided profile.
        """
        ...

    def run(self, ctx: TaskContext) -> bool:
        """
        Executes the task.

        Returns:
            bool: True when the task completed successfully, False otherwise.
        """
        ...
