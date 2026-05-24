---
title: FileChange
description: Representación estructurada de un diff de archivo.
sidebar_position: 1
---

# Clase `FileChange`

## Descripción general

Objeto de datos que representa un cambio de archivo detectado en un diff de git. Es el límite entre el historial git crudo y el razonamiento del LLM.

## Constructor

```python
@dataclass
class FileChange:
    filename: str
    added_lines: list[str]
    removed_lines: list[str]
    hunks: list[str]
    change_summary: str
```

## Atributos

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `filename` | `str` | Ruta relativa al repositorio del archivo modificado. |
| `added_lines` | `list[str]` | Líneas añadidas sin el marcador de diff. |
| `removed_lines` | `list[str]` | Líneas eliminadas sin el marcador de diff. |
| `hunks` | `list[str]` | Líneas de diff crudas preservadas para construcción de prompts. |
| `change_summary` | `str` | Resumen legible del cambio usado en logs y prompts. |

## Uso

Se instancia en `_build_change()` dentro de `git.diff`.

## Dependencias

- `src.config.models`: Definición de la dataclass.