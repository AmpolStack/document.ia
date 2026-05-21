---
title: Diff Parser
description: Extracción y normalización de diffs de git.
sidebar_position: 2
---

# Módulo `src/diff_parser.py`

## Descripción general

Convierte el historial del repositorio en una representación amigable para prompts que el resto del pipeline puede procesar. Se enfoca en `src/` porque el proyecto trata los cambios en código fuente como el desencadenante de actualizaciones de documentación.

**Implicaciones para el proyecto:**
- El rango de commits seleccionado define qué considera el bot como "trabajo nuevo".
- La forma y tamaño del diff generado influyen fuertemente en la calidad del LLM.
- Esta capa es textual y agnóstica al lenguaje, por lo que es simple y robusta, pero no puede inferir semántica más allá de lo que expone el diff.

## Funciones públicas

### `get_structured_diff(base_ref, target_ref, path)`

Extrae cambios estructurados entre dos referencias git.

- **Argumentos:**
  - `base_ref` (str): Referencia base de comparación. Por defecto `DEFAULT_GIT_BASE_REF`.
  - `target_ref` (str): Referencia objetivo. Por defecto `"HEAD"`.
  - `path` (str): Subruta del repositorio a analizar. Por defecto `"src/"`.
- **Retorna:** `list[FileChange]` – lista de objetos que representan archivos modificados.
- **Errores:** Lanza `RuntimeError` si falla el comando git.

### `get_current_head()`

Retorna el hash del commit HEAD actual.

- **Retorna:** `str` – hash del commit.

### `resolve_diff_base(last_processed_commit)`

Resuelve la base de git adecuada para la siguiente ejecución de documentación.

- **Argumentos:**
  - `last_processed_commit` (Optional[str]): Último commit procesado.
- **Retorna:** `Optional[str]` – base de diff, o `None` si HEAD ya fue procesado.

### `format_diff_for_prompt(changes, max_lines_per_file)`

Renderiza los cambios estructurados en un string markdown compacto para el prompt del LLM.

- **Argumentos:**
  - `changes` (list[FileChange]): Cambios a serializar.
  - `max_lines_per_file` (int): Máximo de líneas de diff retenidas por archivo. Por defecto `DIFF_MAX_LINES_PER_FILE`.
- **Retorna:** `str` – texto markdown apto para prompt.

## Funciones internas

### `_parse_diff(raw)`

Parsea la salida cruda de `git diff` en objetos `FileChange`.

### `_build_change(filename, added, removed, hunks)`

Construye un objeto `FileChange` a partir de fragmentos de diff.
