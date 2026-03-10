# Controller

Este módulo contém a camada de orquestração entre interface, profiles e runtime.

## Objetivo

Centralizar as ações operacionais de alto nível da aplicação, evitando que a UI converse diretamente com serviços de baixo nível.

## Componente atual

### `bot_controller.py`
Responsável por:

- carregar e recarregar profiles
- validar pré-execução
- iniciar runtime
- pausar runtime
- retomar runtime
- parar runtime
- refletir estado no `StateStore`
- emitir eventos no `EventBus`

## Observação

Nesta fase, o controller ainda não executa tasks reais nem loop operacional.
Ele apenas controla o ciclo de vida lógico do runtime.