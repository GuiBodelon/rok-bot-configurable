from __future__ import annotations

from typing import Dict, List

from core.tasks.base.task_contract import TaskContract


class TaskRegistryError(Exception):
    """Base error for task registry failures."""


class TaskRegistry:
    """
    Central registry for all available tasks.

    Responsibilities:
    - register task instances
    - prevent duplicate task IDs
    - expose lookup methods
    - provide the list of available tasks to higher-level layers
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskContract] = {}

    def register(self, task: TaskContract) -> None:
        """
        Registers a task instance.

        Raises:
            TaskRegistryError: If the task does not comply with the contract
            or if another task with the same ID is already registered.
        """
        if not isinstance(task.id, str) or not task.id.strip():
            raise TaskRegistryError("Task ID must be a non-empty string.")

        if not isinstance(task.display_name, str) or not task.display_name.strip():
            raise TaskRegistryError("Task display_name must be a non-empty string.")

        if task.id in self._tasks:
            raise TaskRegistryError(f"Task '{task.id}' is already registered.")

        self._tasks[task.id] = task

    def unregister(self, task_id: str) -> None:
        """
        Removes a task from the registry.

        Raises:
            TaskRegistryError: If the task is not registered.
        """
        if task_id not in self._tasks:
            raise TaskRegistryError(f"Task '{task_id}' is not registered.")

        del self._tasks[task_id]

    def get(self, task_id: str) -> TaskContract:
        """
        Returns a registered task by ID.

        Raises:
            TaskRegistryError: If the task is not registered.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskRegistryError(f"Task '{task_id}' is not registered.")

        return task

    def has(self, task_id: str) -> bool:
        """
        Returns whether a task is registered.
        """
        return task_id in self._tasks

    def all(self) -> List[TaskContract]:
        """
        Returns all registered tasks.
        """
        return list(self._tasks.values())

    def ids(self) -> List[str]:
        """
        Returns the list of registered task IDs.
        """
        return sorted(self._tasks.keys())

    def count(self) -> int:
        """
        Returns the number of registered tasks.
        """
        return len(self._tasks)

    def clear(self) -> None:
        """
        Removes all registered tasks.
        """
        self._tasks.clear()

    def describe(self) -> List[Dict[str, str]]:
        """
        Returns a lightweight description of registered tasks.

        Useful for future UI listing and debug output.
        """
        return [
            {
                "id": task.id,
                "display_name": task.display_name,
            }
            for task in self.all()
        ]
