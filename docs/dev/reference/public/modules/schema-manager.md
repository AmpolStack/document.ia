---
title: Schema Manager
description: Módulo para la carga y gestión del esquema de documentación.
sidebar_position: 1
---

# Schema Manager

## Descripción general

El módulo `schema_manager` se encarga de cargar el esquema de documentación desde un archivo YAML (`schema.yml`). Proporciona la función pública `load_schema`, que puede crear un esquema por defecto si se solicita. Es utilizado por el pipeline de generación de documentación para conocer la estructura esperada.

## Funciones públicas

### `load_schema(ensure=False) -> dict`

Carga y analiza el esquema de documentación.

- **Parámetros:**
  - `ensure` (bool): Si es `True` y el archivo de esquema no existe, se crea un esquema por defecto antes de cargarlo.
- **Retorna:** `dict` – Diccionario con la definición del esquema.
- **Excepciones:**
  - `FileNotFoundError`: Si el archivo no existe y `ensure=False`.

## Uso de ejemplo

```python
from src.schema_manager import load_schema

schema = load_schema(ensure=True)
print(schema)
```

## Símbolos relacionados

- `inventory_manager.get_inventory` – para recolectar documentos existentes.
- `src.config.SCHEMA_PATH` – ruta al archivo de esquema.
