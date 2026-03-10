# Runtime

Este módulo contém a base de execução da aplicação.

## Componentes iniciais

- `state_store.py`: fonte única de verdade do estado do runtime
- `event_bus.py`: barramento simples de eventos em memória

## Objetivo

Permitir que camadas como controller, engine e UI conversem de forma desacoplada.

## Papéis

### StateStore
Mantém o estado atual da execução, como:
- running
- paused
- current_task
- current_action
- selected_tasks
- cooldowns
- fail_streaks

### EventBus
Permite publicar e escutar eventos como:
- `runtime.started`
- `runtime.paused`
- `runtime.stopped`
- `task.started`
- `task.finished`
- `action.failed`
- `log.info`

## Observação

Neste estágio, o módulo ainda não executa o bot. Ele apenas fornece a fundação para o runtime real.