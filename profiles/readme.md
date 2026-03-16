# Profiles

This folder contains the product configuration foundation.

## Goal

Decouple the bot from a fixed machine setup, allowing each user to have their own execution profile.

## Structure

- `schemas/`: versioned profile schemas
- `storage/`: locally saved profiles
- `manager.py`: loading, persistence, and basic validation

## Rules

- every profile must define `schema_version`
- coordinates and regions should evolve toward a game-window-relative format
- each task will have its own configuration under `tasks`