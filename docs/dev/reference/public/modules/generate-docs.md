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
- El módulo mezcla intencionadamente comprobaciones deterministas con juicio del LLM para que el sistema siga siendo flexible sin volverse completamente no restringido.
- Los cambios aquí afectan costo, comportamiento de duplicación, seguridad en CI y la experiencia de revisión de desarrolladores en la rama de documentación dedicada.

## Funciones públicas

### `load_schema()`

Carga y parsea el esquema de documentación del proyecto.

- **Retorna:** `dict` – configuración del esquema.
- **Errores:** Lanza `FileNotFoundError` si `schema.yml` no existe.

### `load_pipeline_state()`

Carga el estado persistido del pipeline desde disco.

- **Retorna:** `dict` – estado actual (contiene el último commit procesado).

### `save_pipeline_state(state)`

Persiste el estado del pipeline en disco para futuras ejecuciones.

### `ensure_schema()`

Asegura que exista `schema.yml`, creando uno por defecto si es necesario.

### `get_docs_tree(base_path, label)`

Lee todos los archivos markdown bajo un directorio raíz de documentación.

- **Argumentos:**
  - `base_path` (Path): Directorio raíz.
  - `label` (str): Etiqueta legible para registros.
- **Retorna:** `dict[str, str]` – mapeo de ruta a contenido.

### `build_docs_inventory(tree)`

Construye un inventario compacto de documentos existentes para el LLM.

- **Argumentos:**
  - `tree` (dict): Árbol de documentos.
- **Retorna:** `str` – texto resumido.

### `normalize_doc_key(value)`

Normaliza una ruta o título en un slug comparable.

### `find_similar_existing_doc(raw_file_path, audience_root)`

Encuentra un archivo de documentación existente con un slug conceptual similar.

### `harden_actions_against_existing_docs(actions)`

Reduce acciones `create` redundantes usando evidencia del sistema de archivos.

### `resolve_safe_docs_path(raw_path)`

Resuelve una ruta proporcionada por el LLM y asegura que permanezca dentro de `docs/`.

- **Argumentos:**
  - `raw_path` (Optional[str]): Ruta sin verificar.
- **Retorna:** `Optional[Path]` – ruta segura resuelta, o `None`.

### `main()`

Ejecuta el pipeline completo de generación de documentación.
