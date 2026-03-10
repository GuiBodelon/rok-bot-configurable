# Controller

This module contains the orchestration layer between profiles, runtime, and task registration.

## Purpose

The controller centralizes high-level operational actions so that the UI does not need to communicate directly with low-level runtime components.

## Current component

### `bot_controller.py`
Responsible for:

- loading and reloading profiles
- unloading the active profile
- validating runtime execution preconditions
- starting runtime execution
- executing a runtime cycle through the runtime engine
- pausing runtime execution
- resuming runtime execution
- stopping runtime execution
- registering and unregistering tasks
- exposing registered tasks for future UI and debug usage
- reflecting runtime changes into the `StateStore`
- emitting events through the `EventBus`

## Notes

At this stage, the controller executes synchronous runtime cycles through the runtime engine.

It does not yet provide:

- background worker orchestration
- scheduling policies
- UI bindings
- calibration flow integration

Those concerns will be added incrementally after the core execution flow is stable.