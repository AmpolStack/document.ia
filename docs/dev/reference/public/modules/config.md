---
title: Configuración del sistema
description: Parámetros de configuración del módulo de configuración.
sidebar_position: 1
---

# Módulo `config`

El módulo `config` define las constantes de configuración del sistema.

## Variables de entorno y constantes

| Variable | Default | Descripción |
|----------|---------|-------------|
| `RAG_SCORE_THRESHOLD` | `0.15` | Umbral de puntuación para RAG. |
| `LLM_API_KEY` | `""` | Clave de API para LLM. Se lee de la variable de entorno `LLM_API_KEY`. |
| `LLM_BASE_URL` | `"https://api.deepseek.com"` | URL base del LLM. |
| `LLM_MODEL` | `"deepseek-v4-flash"` | Modelo del LLM. |
| `LLM_TEMPERATURE` | `0.1` | Temperatura del LLM. |
| `LLM_MAX_TOKENS` | `10000` | Máximo de tokens en la respuesta del LLM. Se lee de la variable de entorno `LLM_MAX_TOKENS`; si no está configurada, usa el valor por defecto `10000`. |
| `DOCS_ROOT` | `ROOT / "docs"` | Directorio raíz de los documentos. |
| `DOC_EXISTING_SIMILARITY_THRESHOLD` | `0.72` | Umbral de similitud para detección de duplicados. |
| `EMBEDDING_MODEL` | `"text-embedding-3-small"` | Modelo de embeddings. |
| `CHUNK_SIZE` | `512` | Tamaño de fragmento para indexación. |
| `CHUNK_OVERLAP` | `24` | Superposición entre fragmentos. |
| `DIFF_MAX_LINES_PER_FILE` | `280` | Límite de líneas de diff por archivo. |

## Notas de mantenimiento

- `LLM_MAX_TOKENS` se ha modificado para ser configurable mediante variable de entorno, manteniendo `10000` como valor predeterminado.
- Todas las constantes que dependen de variables de entorno se evalúan al cargar el módulo.