# RoK Bot Configurable

Desktop application for configurable automation in Rise of Kingdoms, focused on:

- graphical interface
- setup-based profiles
- guided calibration
- controlled runtime
- modular tasks

## Goal

Turn a bot originally coupled to a single machine setup into a configurable, versioned desktop product.

## Initial stack

- Python
- PySide6
- JSON for profiles
- PyInstaller for packaging

## Initial structure

- `app/` application bootstrap
- `core/` runtime, controller, tasks, and services
- `ui/` desktop interface
- `calibration/` onboarding and calibration
- `profiles/` schemas, migrations, and storage
- `docs/` project documentation

## Status

Currently in the initial architecture phase.