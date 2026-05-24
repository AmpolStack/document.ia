---
title: Sincronización del Sitio de Documentación
description: Módulo para mantener índices navegables.
sidebar_position: 1
---

# Módulo `docs.sync`

## Descripción general

Genera o actualiza páginas índice (index.md) para cada directorio bajo `docs/`, asegurando que el sitio de documentación estático sea navegable.

## Función pública

### `sync_docs_site_indexes()`

Recorre recursivamente todos los directorios bajo `docs/` y genera o actualiza sus respectivos `index.md` con frontmatter y enlaces a subsecciones y documentos.

- **Retorna:** `list[Path]` – lista de rutas de índices actualizados.
- **Marcador:** Los archivos generados contienen `<!-- AUTO-GENERATED: docs-site-sync -->`.

## Funciones internas

- `_title_from_dir(directory)` – Título legible según la carpeta.
- `_description_from_dir(directory)` – Descripción para frontmatter.
- `_build_frontmatter(directory)` – Construye el frontmatter YAML.
- `_build_section(title, items)` – Construye sección con enlaces.
- `build_index_content(directory)` – Contenido completo del índice.

## Notas

- Los archivos índice se sobrescriben si comienzan con el marcador gestionado.
- No modifica archivos que no estén marcados como gestionados.
- Soporta Docusaurus, MkDocs y otros generadores.