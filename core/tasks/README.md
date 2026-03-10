# Tasks

This module defines the operational task model of the application.

## Purpose

Tasks represent the executable units of the bot, such as:

- farm
- scout
- train
- alliance help
- future flows like caves or other guided automation steps

## Components

### `base/task_contract.py`
Defines the protocol that every task must implement.

### `base/task_context.py`
Defines the runtime context passed to tasks during execution.

### `registry.py`
Provides the central registry used to register, discover, and retrieve tasks.

### Concrete task stubs
The module now includes placeholder implementations for:

- `FarmTask`
- `ScoutTask`
- `TrainTask`
- `AllianceHelpTask`

These stubs do not execute real automation yet.
They establish official task IDs, configuration expectations, and calibration step structure.

## Design goals

- keep task execution decoupled from the UI
- formalize task requirements before implementing real task logic
- allow future runtime and controller layers to operate against a stable contract
- support calibration and validation flows per task

## Notes

Concrete task implementations are still placeholders at this stage.
Their purpose is to stabilize the architecture before real automation logic is introduced.