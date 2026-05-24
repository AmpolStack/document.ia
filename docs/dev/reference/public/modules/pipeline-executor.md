---
title: Ejecutor de Pipeline
description: Función para ejecutar acciones decididas por el LLM en el sistema de archivos.
sidebar_position: 1
---

# Módulo `pipeline.executor`

## Overview

Este módulo contiene la función `execute_actions` que toma una lista de acciones (generadas por el LLM) y las ejecuta en el sistema de archivos, creando, actualizando o eliminando archivos de documentación.

## Función pública

### `execute_actions(actions)`

Ejecuta una lista de acciones de documentación.

- **Firma:** `def execute_actions(actions: List[dict]) -> List[str]`
- **Parámetros:** `actions` – lista de diccionarios con las claves `type`, `audience`, `file`, `content`.
- **Retorna:** Lista de rutas de archivos que fueron procesados exitosamente.
- **Descripción:** Itera sobre las acciones. Para cada acción, verifica que la ruta del archivo esté dentro del directorio `docs/` usando normalización de ruta con `os.path.normpath` para prevenir ataques de path traversal. Si la acción es `create` o `update`, crea los directorios padres necesarios y escribe el contenido. Si es `delete`, elimina el archivo. Registra advertencias para rutas inseguras.
- **Errores:** No lanza excepciones; ignora acciones con rutas inseguras.
- **Uso:** Esta función es llamada por el pipeline principal después de que el LLM decide las acciones.

## Símbolos relacionados

- [Decisor de LLM](../modules/llm-decider.md) – genera las acciones.
- [RAG Manager](../modules/rag-manager.md) – actualiza índices después de ejecución.
