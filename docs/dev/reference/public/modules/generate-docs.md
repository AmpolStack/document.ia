---
title: Generate Docs
description: Orquestador principal del pipeline de generación de documentación.
sidebar_position: 4
---

# Módulo `src/generate_docs.py`

## Descripción general

Coordina el flujo completo del proyecto:
1. Resuelve el rango de commits que aún necesita documentación.
2. Extrae cambios de código fuente de `src/`.
3. Lee e inventaria la documentación markdown existente.
4. Recupera contexto semántico relevante del almacén de vectores.
5. Solicita al LLM las acciones de documentación necesarias.
6. Refuerza esas acciones contra redundancias obvias.
7. Persiste las actualizaciones markdown y actualiza el almacén de vectores.
8. Mantiene las páginas índice del sitio estático bajo `docs/`.

**Implicaciones para el proyecto:**
- Este archivo es el corazón operativo. La mayoría de las preguntas "¿por qué el bot documentó esto?" se remontan a decisiones tomadas aquí.

---

## Funciones públicas

### `get_docs_tree(base_path, label)`

Lee todos los archivos markdown bajo un directorio raíz de documentación.

- **Argumentos:**
  - `base_path` (Path): Directorio raíz.
  - `label` (str): Etiqueta legible para registros.
- **Retorna:** `dict[str, str]` – mapeo de ruta a contenido.

### `build_docs_inventory(docs_tree)`

Construye un inventario compacto de documentos existentes para el LLM. Esta función se introdujo para mejorar la conciencia contextual del LLM sobre qué documentación ya existe, reduciendo acciones redundantes.

- **Argumentos:**
  - `docs_tree` (dict[str, str]): Árbol de documentos obtenido de `get_docs_tree`.
- **Retorna:** `str` – texto resumido con las rutas de los archivos ordenadas alfabéticamente.
- **Comportamiento:** Devuelve una cadena vacía si el árbol está vacío.

### `normalize_doc_key(value)`

Normaliza una ruta o título en un slug comparable.

### `find_similar_existing_doc(raw_file_path, audience_root)`

Encuentra un archivo de documentación existente con un slug conceptual similar.

### `harden_actions_against_existing_docs(actions)`

Reduce acciones `create` redundantes usando evidencia del sistema de archivos.

### `main()`

Ejecuta el pipeline de generación de documentación. Desde la versión actual, realiza los siguientes pasos adicionales:
1. Obtiene los árboles de documentación existentes para desarrollador y usuario mediante `get_docs_tree`.
2. Construye inventarios compactos con `build_docs_inventory`.
3. Imprime el resumen de archivos encontrados.
4. Pasa estos inventarios a `decide_actions` para que el LLM tenga conciencia de la documentación existente.

**Cambios recientes:**
- Se agregó la construcción de inventarios (`dev_docs_inventory`, `user_docs_inventory`) y su uso en el llamado a `decide_actions`.
- La función `decide_actions` ahora acepta dos parámetros adicionales: `dev_docs_inventory` y `user_docs_inventory`.

---

## Funciones internas

No hay funciones internas nuevas en este cambio.

---

## Relacionados

- `decide_actions` en `modules/llm-decider.md`
- `get_docs_tree`