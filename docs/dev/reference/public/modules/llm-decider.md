---
title: LLM Decider
description: Capa de decisión del LLM para planificación de documentación.
sidebar_position: 5
---

# Módulo `src/llm_decider.py`

## Descripción general

Convierte el contexto del repositorio en un prompt para el LLM y transforma la respuesta en acciones estructuradas de documentación. No escribe archivos por sí mismo; proporciona el límite de razonamiento entre las entradas deterministas del proyecto y la ejecución descendente.

**Implicaciones para el proyecto:**
- La redacción del prompt aquí influye fuertemente en si el sistema prefiere no-op, update o create.
- Es uno de los módulos de mayor apalancamiento: pequeños cambios en las instrucciones pueden cambiar los resultados de documentación en cada ejecución de CI.
- Debido a que el proyecto depende de respuestas solo JSON, la claridad del prompt y la robustez del parseo afectan directamente la confiabilidad de la automatización.

*(No se han modificado funciones específicas en el diff más allá de la documentación del módulo.)*
