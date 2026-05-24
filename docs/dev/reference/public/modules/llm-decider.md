---
title: Decisor LLM
description: Módulo para construir prompts y comunicarse con el LLM.
sidebar_position: 1
---

# Módulo `llm`

## Descripción general

Construye el prompt de decisión, envía la consulta al LLM y parsea la respuesta JSON para obtener las acciones de documentación.

## Funciones públicas

### `build_prompt(diff_text, contexts, inventories)`

Construye el prompt completo para el LLM.

- **Parámetros:**
  - `diff_text` (str): Diff formateado.
  - `contexts` (dict[str, str]): Contexto relevante por audiencia.
  - `inventories` (dict[str, str]): Inventario de archivos existentes por audiencia.
- **Retorna:** `str` – prompt listo para enviar.

### `call_llm(prompt)`

Envía el prompt al LLM configurado y retorna la respuesta cruda.

- **Parámetros:**
  - `prompt` (str): Prompt completo.
- **Retorna:** `str` – respuesta del LLM.

### `parse_llm_response(raw)`

Extrae y parsea el bloque JSON de acciones de la respuesta del LLM.

- **Parámetros:**
  - `raw` (str): Respuesta cruda del LLM.
- **Retorna:** `list[dict]` – lista de acciones.
- **Errores:** Lanza `ValueError` si no encuentra JSON.

### `decide_actions(prompt)`

Función combinada: envía el prompt, parsea la respuesta y retorna las acciones.

- **Parámetros:**
  - `prompt` (str): Prompt completo.
- **Retorna:** `list[dict]` – lista de acciones.

## Dependencias

- `src.llm.prompt`: `build_prompt`
- `src.llm.client`: `call_llm`, `parse_llm_response`, `decide_actions`