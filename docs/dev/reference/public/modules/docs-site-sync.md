---
title: Docs Site Sync
description: Sincronización de páginas índice para generadores de sitios estáticos.
sidebar_position: 3
---

# Módulo `src/docs_site_sync.py`

## Descripción general

Mantiene páginas de aterrizaje bajo `docs/` para que el markdown generado sea utilizable tanto en el repositorio como en generadores de sitios como Docusaurus.

**Implicaciones para el proyecto:**
- La calidad de la documentación no solo depende del contenido, sino también de la navegabilidad para revisores y usuarios finales.
- Las páginas de aterrizaje generadas crean una segunda capa de documentación derivada que debe mantenerse consistente con las páginas markdown primarias.
- Dado que estas páginas también pueden ser indexadas en el almacén de vectores, la navegación y el comportamiento de recuperación están indirectamente conectados.

## Funciones públicas

*(No se definen funciones públicas en el diff, pero el módulo exporta funciones para sincronizar índices.)*
