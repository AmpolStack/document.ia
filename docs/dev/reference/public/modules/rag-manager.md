---
title: RAG Manager
description: Capa RAG para indexación y recuperación de contexto de documentación.
sidebar_position: 6
---

# Módulo `src/rag_manager.py`

## Descripción general

Gestiona el lado del almacén de vectores del proyecto. Indexa documentos markdown en ChromaDB, configura la pila de embeddings y recupera los fragmentos de documentación más relevantes para un diff dado.

**Implicaciones para el proyecto:**
- Este es el sistema de memoria del pipeline. Sin una recuperación fuerte, el LLM se comporta como si el proyecto tuviera poca o ninguna documentación previa.
- Los umbrales de recuperación influyen en el comportamiento de duplicación casi tanto como la redacción del prompt.
- Debido a que el almacén de vectores se almacena en caché en CI, la consistencia entre el estado del disco y el estado del índice es importante para la corrección en varias ejecuciones.

## Funciones públicas

### `configure_llamaindex()`

Configura los ajustes globales de LlamaIndex (LLM, modelo de embeddings, splitter de texto).

- **Errores:** Lanza `ValueError` si `DEEPSEEK_API_KEY` no está configurada.

### `index_docs(audience, filepath, replace=True)`

Indexa un archivo markdown en el almacén de vectores.

- **Argumentos:**
  - `audience` (str): Audiencia (`'dev'` o `'user'`).
  - `filepath` (str): Ruta al archivo markdown.
  - `replace` (bool): Si se deben reemplazar entradas anteriores del mismo archivo.

### `is_collection_empty(audience)`

Verifica si la colección para una audiencia está vacía.

- **Retorna:** `bool`.

### `query_relevant_context(query, audience, n_results=3)`

Recupera fragmentos de documentación relevantes basados en similitud semántica.

- **Argumentos:**
  - `query` (str): Texto de búsqueda (normalmente el diff formateado).
  - `audience` (str): Audiencia.
  - `n_results` (int): Máximo de fragmentos a recuperar.
- **Retorna:** `str` – fragmentos concatenados, o cadena vacía.

## Funciones internas

### `_get_chroma_collection(audience)`

Obtiene o crea una colección ChromaDB para una audiencia.

### `_chunk_markdown_smart(text)`

Divide markdown en fragmentos respetando la estructura de secciones.
