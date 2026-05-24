---
title: Gestor de Inventario
description: Módulo para inspeccionar archivos de documentación existentes.
sidebar_position: 1
---

# Módulo `docs.inventory`

## Descripción general

Proporciona funciones para recolectar y resumir los archivos markdown existentes en un directorio de documentación, usado por el construcctor de prompts para evitar duplicados.

## Funciones públicas

### `get_inventory(base_path, label)`

Recolecta todos los archivos `.md` de un directorio de documentación.

- **Parámetros:**
  - `base_path` (Path): Ruta raíz de la documentación.
  - `label` (str): Etiqueta para logging.
- **Retorna:** `dict[str, str]` – mapeo de rutas a contenidos.

### `compact_inventory(docs_tree)`

Construye una cadena compacta con las rutas de archivos ordenadas alfabéticamente.

- **Parámetros:**
  - `docs_tree` (dict[str, str]): Mapeo de rutas a contenidos.
- **Retorna:** `str` – inventario plano, cada ruta en una línea.