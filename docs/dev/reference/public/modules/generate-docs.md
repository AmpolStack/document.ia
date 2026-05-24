---
title: Generación de Documentación
description: Orquestador y ejecutor del pipeline de documentación.
sidebar_position: 1
---

# Módulo `pipeline`

## Descripción general

Contiene la lógica de orquestación y ejecución del pipeline de documentación. El punto de entrada principal es `python -m src`.

## Orquestador (`orchestrator.py`)

### `run()`

Ejecuta el pipeline completo:
1. Carga el esquema de documentación.
2. Configura el RAG.
3. Resuelve la base de diff (último commit procesado).
4. Obtiene los cambios de git estructurados.
5. Recupera contexto relevante de documentación existente.
6. Construye el prompt y llama al LLM.
7. Ejecuta las acciones decididas (crear, actualizar, eliminar).
8. Guarda el estado del último commit procesado.

**Nota:** El pipeline termina sin errores si no hay cambios o si HEAD ya fue procesado.

### Estado del pipeline
- Archivo: `.doc_pipeline_state.json` (en la raíz del proyecto)
- Contiene `last_commit` – hash del último commit procesado.

## Ejecutor (`executor.py`)

### `execute_actions(actions)`

Aplica las acciones decididas por el LLM al sistema de archivos.

- **Parámetros:**
  - `actions` (list[dict]): Lista de acciones (create, update, delete).
- **Retorna:** `list[str]` – rutas de archivos creados o actualizados.
- **Seguridad:** Rechaza rutas que no comiencen con `docs/`.
- **Efectos secundarios:** Actualiza el índice de vectores tras generación.

## Punto de entrada (`__main__.py`)

Ejecuta `main()` que:
1. Configura logging con `configure_logging()`.
2. Llama a `run()` del orquestador.
3. Captura excepciones fatales y termina con código 1.

## Logging (`_logging.py`)

### `configure_logging(level)`

Configura el logging global con formato estándar.

- **Parámetros:**
  - `level` (int): Nivel de logging (por defecto `logging.INFO`).

## Dependencias

- `src.config.settings`: rutas, RAG_*, LLM_*
- `src.config.models`: AUDIENCES
- `src.git.diff`: get_structured_diff, format_diff_for_prompt, resolve_diff_base, get_current_head
- `src.llm.prompt`: build_prompt
- `src.llm.client`: decide_actions
- `src.rag.*`: configuración, indexación, recuperación
- `src.pipeline.executor`: execute_actions