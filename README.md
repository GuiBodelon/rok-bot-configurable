# RoK Bot Configurable

Aplicação desktop para automação configurável no Rise of Kingdoms, com foco em:

- interface gráfica
- perfis por setup
- calibração guiada
- runtime controlado
- tasks modulares

## Objetivo

Transformar um bot originalmente acoplado a um setup único em um produto desktop configurável e versionado.

## Stack inicial

- Python
- PySide6
- JSON para perfis
- PyInstaller para empacotamento

## Estrutura inicial

- `app/` bootstrap da aplicação
- `core/` runtime, controller, tasks e serviços
- `ui/` interface desktop
- `calibration/` onboarding e calibração
- `profiles/` schemas, migrations e armazenamento
- `docs/` documentação do projeto

## Status

Em arquitetura inicial.