---
title: Decisor de LLM
description: Funciones para interactuar con el LLM y decidir acciones.
sidebar_position: 1
---

# Módulo `llm_decider`

## Overview

Este módulo proporciona las funciones principales para comunicarse con el LLM y procesar sus respuestas para decidir las acciones a realizar.

## Funciones públicas

### `call_llm(prompt)`

Envía un prompt al LLM configurado y devuelve la respuesta en texto plano.

- **Firma:** `def call_llm(prompt: str) -> str`
- **Parámetros:** `prompt` – texto del prompt.
- **Retorna:** Respuesta del LLM como cadena.
- **Errores:** Puede lanzar excepciones de conexión.
- **Uso:** Ver ejemplo en `decide_actions`.

### `parse_llm_response(raw)`

Extrae y analiza el bloque JSON de acciones de la respuesta del LLM.

- **Firma:** `def parse_llm_response(raw: str) -> List[Dict[str, Any]]`
- **Parámetros:** `raw` – respuesta completa del LLM.
- **Retorna:** Lista de diccionarios de acciones.
- **Descripción:** Esta función busca un bloque JSON (entre llaves) en la respuesta cruda. Luego limpia caracteres de escape inválidos que el LLM suele generar (como `\`, `\-`, continuación de línea) usando una función interna `_clean_json_text`. Posteriormente parsea el JSON con `json.loads`. Si no se encuentra JSON, lanza `ValueError`.
- **Errores:** `ValueError` si no hay JSON en la respuesta.
- **Uso:** Ver `decide_actions`.

### `decide_actions(prompt)`

Función completa que envía un prompt, parsea la respuesta y retorna la lista de acciones.

- **Firma:** `def decide_actions(prompt: str) -> List[Dict[str, Any]]`
- **Parámetros:** `prompt` – texto del prompt.
- **Retorna:** Lista de acciones.
- **Descripción:** Llama a `call_llm` y luego a `parse_llm_response`.
- **Uso:** Esta es la función principal para obtener acciones del LLM.

## Símbolos relacionados

- [Cliente LLM interno](../internal/modules/llm-client.md) – para la función de limpieza interna.
