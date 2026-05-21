---
title: Config
description: Configuración central del pipeline de documentación.
sidebar_position: 1
---

# Módulo `src/config.py`

## Descripción general

Define la configuración compartida utilizada en ejecuciones locales y en GitHub Actions. Centraliza rutas de archivos, comportamiento del LLM, umbrales de recuperación, tamaño de diff y heurísticas de deduplicación para que el proyecto no dependa de valores hardcodeados dispersos.

**Implicaciones para el proyecto:**
- Los cambios en la configuración pueden alterar el costo, la precisión y el comportamiento de duplicación sin modificar el resto del código.
- Centralizar estos valores mejora la revisabilidad y hace que el comportamiento de CI sea más fácil de razonar.
- El proyecto trata estas constantes como parte de su superficie de políticas, especialmente en cuanto a agresividad de recuperación y tamaño de prompts.

## Constantes

| Nombre | Valor | Descripción |
|--------|-------|-------------|
| `PROJECT_ROOT` | Path(__file__).resolve().parent.parent | Raíz del proyecto. |
| `DOCS_DEV_DIR` | PROJECT_ROOT / "docs" / "dev" | Directorio de documentación para desarrolladores. |
| `DOCS_USER_DIR` | PROJECT_ROOT / "docs" / "user" | Directorio de documentación para usuarios finales. |
| `SCHEMA_PATH` | PROJECT_ROOT / "docs" / "schema.yml" | Ruta al archivo de esquema. |
| `PIPELINE_STATE_PATH` | PROJECT_ROOT / "pipeline_state.json" | Ruta al archivo de estado del pipeline. |
| `VECTOR_STORE_PATH` | PROJECT_ROOT / "vector_store" | Ruta al almacén de vectores ChromaDB. |
| `DEFAULT_GIT_BASE_REF` | "origin/main" | Referencia base por defecto para diff. |
| `RAG_TOP_K` | 3 | Número de fragmentos recuperados por consulta RAG. |
| `LLM_MODEL` | "deepseek-chat" | Modelo LLM utilizado. |
| `LLM_TEMPERATURE` | 0.0 | Temperatura del LLM. |
| `LLM_MAX_TOKENS` | 2048 | Máximo de tokens en la respuesta del LLM. |
| `EMBEDDING_MODEL` | "text-embedding-3-small" | Modelo de embeddings. |
| `CHUNK_SIZE` | 512 | Tamaño de fragmento para indexación. |
| `CHUNK_OVERLAP` | 24 | Superposición entre fragmentos. |
| `DIFF_MAX_LINES_PER_FILE` | 280 | Límite de líneas de diff por archivo. |
| `DOC_EXISTING_SIMILARITY_THRESHOLD` | 0.72 | Umbral de similitud para detección de duplicados. |

## Clase pública `FileChange`

Ver [FileChange](../classes/file-change.md).
