# Architectural Decisions

## ADR-001 — UI Framework
Escolhido: PySide6

Motivo:
- UI desktop mais robusta
- melhor escalabilidade
- melhor experiência visual

## ADR-002 — Perfil por JSON
Escolhido: JSON versionado

Motivo:
- simples
- fácil de editar
- fácil de migrar
- ótimo para fase inicial

## ADR-003 — Coordenadas relativas à janela
Escolhido: tudo relativo à janela do jogo

Motivo:
- reduz acoplamento ao monitor
- melhora portabilidade entre setups