---
title: Gestor RAG
description: Módulo para indexación, recuperación y configuración del RAG.
sidebar_position: 1
---

# Módulo `rag`

## Descripción general

Proporciona toda la funcionalidad de Retrieval-Augmented Generation: chunking, indexación en ChromaDB, consultas semánticas y configuración de embeddings/LLM.

## Configuración (`setup.py`)

### `configure()`

Configura los ajustes globales de LlamaIndex (LLM, embedding model, text splitter).

- **Errores:** Lanza `ValueError` si `LLM_API_KEY` no está definida.

## Fragmentación (`chunker.py`)

### `chunk_markdown(text)`

Divide texto markdown en fragmentos respetando secciones (`##`).

- **Parámetros:**
  - `text` (str): Contenido markdown.
- **Retorna:** `list[str]` – fragmentos.

## Indexación (`indexer.py`)

### `get_chroma_collection(audience)`

Obtiene o crea la colección ChromaDB para una audiencia.

- **Parámetros:**
  - `audience` (str): Etiqueta de audiencia.
- **Retorna:** `tuple` – (vector_store, collection_name).

### `index_docs(audience, filepath, replace)`

Indexa un archivo markdown en el almacén de vectores.

- **Parámetros:**
  - `audience` (str): Etiqueta de audiencia.
  - `filepath` (str): Ruta al archivo.
  - `replace` (bool): Si elimina nodos antiguos (por defecto `True`).

### `index_directory(audience, directory)`

Indexa todos los archivos markdown de un directorio.

- **Parámetros:**
  - `audience` (str): Etiqueta de audiencia.
  - `directory` (str): Ruta del directorio.

### `is_collection_empty(audience)`

Verifica si la colección está vacía.

- **Retorna:** `bool`.

### `update_index_after_generation(paths)`

Reindexa archivos generados, reemplazando versiones anteriores.

- **Parámetros:**
  - `paths` (list[str]): Lista de rutas a indexar.

### `delete_docs_by_source(audience, source_path)`

Elimina nodos indexados cuyo `source` coincida.

- **Parámetros:**
  - `audience` (str): Etiqueta de audiencia.
  - `source_path` (str): Ruta del archivo fuente.
- **Retorna:** `int` – número de nodos eliminados.

## Recuperación (`retriever.py`)

### `query_relevant_context(query, audience, n_results)`

Recupera fragmentos relevantes del almacén de vectores.

- **Parámetros:**
  - `query` (str): Texto de búsqueda, normalmente el diff formateado.
  - `audience` (str): Etiqueta de audiencia.
  - `n_results` (int): Número máximo de fragmentos (por defecto `RAG_TOP_K`).
- **Retorna:** `str` – fragmentos concatenados o cadena vacía si no hay resultados relevantes.