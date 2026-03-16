# Architectural Decisions

## ADR-001 — UI Framework
Selected: PySide6

Reason:
- More robust desktop UI
- Better scalability
- Better visual experience

## ADR-002 — JSON-based profile
Selected: Versioned JSON

Reason:
- Simple
- Easy to edit
- Easy to migrate
- Great for the initial phase

## ADR-003 — Window-relative coordinates
Selected: Everything relative to the game window

Reason:
- Reduces monitor coupling
- Improves portability across setups