---
title: Analizador de Diff
description: Módulo para extraer y normalizar cambios de git.
sidebar_position: 1
---

# Módulo `git.diff`

## Descripción general

Extrae el diff estructurado entre dos referencias de git y lo convierte en objetos `FileChange` listos para el pipeline de documentación.

## Funciones públicas

### `get_structured_diff(base_ref, target_ref, path)`

Obtiene los cambios estructurados entre dos referencias de git.

- **Parámetros:**
  - `base_ref` (str): Referencia base (por defecto `DEFAULT_GIT_BASE_REF`).
  - `target_ref` (str): Referencia objetivo (por defecto `"HEAD"`).
  - `path` (str): Subruta a analizar (por defecto `"src/"`).
- **Retorna:** `list[FileChange]` – lista de cambios.
- **Errores:** Lanza `RuntimeError` si falla el comando git.

### `get_current_head()`

Retorna el hash del commit HEAD actual.

- **Retorna:** `str` – hash del commit.

### `resolve_diff_base(last_processed_commit)`

Resuelve la base de diff para la siguiente ejecución. Retorna `None` si HEAD ya fue procesado.

- **Parámetros:**
  - `last_processed_commit` (Optional[str]): Último commit procesado.
- **Retorna:** `Optional[str]` – base de diff o `None`.

### `format_diff_for_prompt(changes, max_lines_per_file)`

Renderiza los cambios en markdown compacto para el prompt del LLM.

- **Parámetros:**
  - `changes` (list[FileChange]): Cambios a serializar.
  - `max_lines_per_file` (int): Máximo de líneas de diff retenidas por archivo. Por defecto `DIFF_MAX_LINES_PER_FILE`.
- **Retorna:** `str` – texto markdown.

## Funciones internas

### `_parse_diff(raw)`

Parsea la salida cruda de `git diff` en objetos `FileChange`.

### `_build_change(filename, added, removed, hunks)`

Construye un `FileChange` a partir de fragmentos de diff.

## Dependencias

- `src.config.settings`: `DEFAULT_GIT_BASE_REF`, `DIFF_MAX_LINES_PER_FILE`
- `src.config.models`: `FileChange`