---
title: Gestor de Esquema
description: Módulo para cargar y gestionar el schema.yml.
sidebar_position: 1
---

# Módulo `docs.schema`

## Descripción general

Carga y gestiona el archivo de esquema de documentación (`schema.yml`). Si no existe, puede crear uno por defecto.

## Funciones públicas

### `load_schema(path, ensure)`

Carga y parsea el schema YAML.

- **Parámetros:**
  - `path` (Path): Ruta al archivo schema.yml.
  - `ensure` (bool): Si es `True`, crea schema por defecto si no existe.
- **Retorna:** `dict` – contenido del schema.
- **Errores:** Lanza `FileNotFoundError` si no existe y `ensure=False`.

### `_ensure_schema(path)` (interna)

Crea un archivo schema.yml por defecto en la ruta indicada.

## Esquema por defecto

- `version: "1.0"`
- `documentation.dev.sections`: API Reference, Architecture, Setup, Contributing
- `documentation.user.sections`: Getting Started, User Guide, FAQ, Troubleshooting