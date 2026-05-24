---
title: Cliente LLM interno
description: Funciones internas de limpieza de JSON para respuestas del LLM.
sidebar_position: 1
---

# Símbolos internos de `llm.client`

## Propósito

Contiene utilidades internas para limpiar y normalizar respuestas JSON del LLM antes de parsearlas.

## Flujo interno

La función `_clean_json_text` es llamada por `parse_llm_response` (en el módulo público `llm_decider`) para eliminar caracteres de escape inválidos que el LLM a menudo incluye, como `\` seguido de caracteres no válidos en JSON, o líneas continuadas.

## Entradas y salidas

- **Entrada:** `text: str` – texto JSON crudo.
- **Salida:** `str` – texto JSON limpio con escapes inválidos eliminados.
- **Algoritmo:** Recorre el texto carácter por carácter. Si encuentra una barra invertida, examina el siguiente carácter: si es uno de los escapes JSON estándar (`"`, `\`, `/`, `b`, `f`, `n`, `r`, `t`, `u`), lo conserva; si es un salto de línea (`\n`, `\r`), lo elimina; de lo contrario, elimina la barra invertida y conserva el carácter siguiente.

## Efectos secundarios

Ninguno.

## Notas de mantenimiento

- Si el LLM cambia su formato de salida, esta función podría necesitar ajustes.
- Asegurarse de que la función no elimine escapes legítimos en cadenas JSON.

## Símbolos relacionados

- [parse_llm_response](../../public/modules/llm-decider.md) – función pública que utiliza esta limpieza.
