# Profiles

Esta pasta contém a base de configuração do produto.

## Objetivo

Desacoplar o bot do setup fixo da máquina, permitindo que cada usuário possua seu próprio perfil de execução.

## Estrutura

- `schemas/`: schemas versionados do profile
- `storage/`: profiles salvos localmente
- `manager.py`: carregamento, persistência e validação básica

## Regras

- todo profile deve possuir `schema_version`
- coordenadas e regions devem evoluir para formato relativo à janela do jogo
- cada task terá configuração própria dentro de `tasks`