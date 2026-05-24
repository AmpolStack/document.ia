---
title: Configuración
description: Módulo de configuración global del proyecto.
sidebar_position: 1
---

# Módulo `config`

## Descripción general

Contiene la configuración centralizada del proyecto, incluyendo ajustes de pipeline, RAG, LLM y modelos de datos.

## Configuración (`settings.py`)

### Constantes

- `ROOT` – raíz del proyecto (`Path.cwd()`)
- `SCHEMA_PATH` – ruta al archivo schema.yml
- `DEFAULT_GIT_BASE_REF` – referencia base por defecto (`"HEAD~1"`)
- `DIFF_MAX_LINES_PER_FILE` – máximo de líneas de diff por archivo (280)
- `CHUNK_SIZE` – tamaño de fragmento para RAG (300)
- `CHUNK_OVERLAP` – solapamiento entre fragmentos (30)
- `VECTOR_STORE_PATH` – ruta al almacén de vectores
- `EMBED_MODEL` – modelo de embeddings (`"sentence-transformers/all-MiniLM-L6-v2"`)
- `EMBED_BATCH_SIZE` – tamaño de lote (10)
- `PIPELINE_STATE_PATH` – ruta al archivo de estado del pipeline
- `RAG_TOP_K` – número de resultados a recuperar (3)
- `RAG_SCORE_THRESHOLD` – umbral de relevancia (0.15)
- `LLM_API_KEY` – clave de API (desde variable de entorno)
- `LLM_BASE_URL` – URL base del LLM (`"https://api.deepseek.com"`)
- `LLM_MODEL` – modelo (`"deepseek-v4-flash"`)
- `LLM_TEMPERATURE` – temperatura (0.1)
- `LLM_MAX_TOKENS` – máximo de tokens (10000)
- `DOCS_ROOT` – raíz de documentación
- `DOC_EXISTING_SIMILARITY_THRESHOLD` – umbral de similitud (0.72)

### Variables de entorno

- `LLM_API_KEY` – requerida en `.env`
- `LLM_MAX_TOKENS` – opcional, por defecto 10000

## Modelos (`models.py`)

### `FileChange`

Clase ya documentada en [FileChange](../classes/file-change.md).

### `DocAction`

Acción decidida por el LLM para aplicar en el árbol de documentación.

- **Atributos:** `type` (str: create|update|delete), `audience` (str), `file` (str), `content` (str)

### `Audience`

Configuración de una audiencia de documentación.

- **Atributos:** `path` (str), `label` (str), `similarity_threshold` (float, por defecto 0.72), `reason` (str)

### `AUDIENCES`

Lista de instancias de `Audience` predefinidas:
- `developer` – docs/dev
- `user` – docs/user