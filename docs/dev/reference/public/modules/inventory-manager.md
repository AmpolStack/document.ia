---
title: Inventory Manager
description: Módulo para la recolección y compactación de inventarios de documentación.
sidebar_position: 1
---

# Inventory Manager

## Descripción general

El módulo `inventory_manager` proporciona funciones para recorrer un directorio raíz de documentación, recolectar todos los archivos Markdown y generar un inventario compacto que pueda ser utilizado como contexto para un LLM. Las funciones reemplazan a las anteriores `get_docs_tree` y `build_docs_inventory`. Este módulo es parte fundamental del pipeline de decisión de documentación.

## Funciones públicas

### `get_inventory(base_path: Path, label: str) -> dict[str, str]`

Recolecta todos los archivos Markdown bajo un directorio raíz.

- **Parámetros:**
  - `base_path` (Path): Directorio raíz donde buscar archivos `.md`.
  - `label` (str): Etiqueta legible para registros (ej. "Developer", "User").
- **Retorna:** `dict[str, str]` – Mapeo de ruta del archivo a su contenido.
- **Excepciones:** No lanza excepciones; si el directorio no existe, retorna un diccionario vacío y registra una advertencia.

### `compact_inventory(docs_tree: dict[str, str]) -> str`

Construye un inventario compacto con las rutas de los archivos ordenadas alfabéticamente.

- **Parámetros:**
  - `docs_tree` (dict[str, str]): Árbol de documentos obtenido de `get_inventory`.
- **Retorna:** `str` – Lista de rutas separadas por saltos de línea, o cadena vacía si el árbol está vacío.

## Uso de ejemplo

```python
from pathlib import Path
from src.inventory_manager import get_inventory, compact_inventory

dev_inventory = get_inventory(Path("docs/dev"), "Developer")
compact = compact_inventory(dev_inventory)
print(compact)
```

## Símbolos relacionados

- `schema_manager.load_schema` – para cargar el esquema de documentación.
- `src.docs_site_sync` – para sincronizar documentación generada.
