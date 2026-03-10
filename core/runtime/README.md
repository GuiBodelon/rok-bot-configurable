# Runtime

This module contains the execution foundation of the application.

## Components

### `state_store.py`
Provides the single source of truth for runtime state.

### `event_bus.py`
Provides an in-memory event bus used by the runtime and higher-level layers.

### `runtime_engine.py`
Executes selected tasks sequentially using the current runtime state and the task registry.

## Purpose

The runtime layer exists to coordinate execution without coupling business flow to the UI.

## Responsibilities

- keep runtime state centralized
- publish runtime and task lifecycle events
- resolve selected tasks from the registry
- build task execution context
- execute tasks in sequence
- track failures at runtime level

## Notes

At this stage, the runtime engine executes a single synchronous cycle through the selected tasks.

It does not yet implement:

- background threads
- infinite execution loop
- scheduling policies
- recovery orchestration
- timing strategies between tasks

Those concerns will be added incrementally after the execution foundation is stable.