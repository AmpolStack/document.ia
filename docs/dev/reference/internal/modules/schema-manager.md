---
title: Schema Manager (Internal)
description: Función interna para asegurar la existencia del esquema por defecto.
sidebar_position: 1
---

# Schema Manager (Internal)

## Propósito

La función interna `_ensure_schema` garantiza que exista un archivo de esquema YAML en `SCHEMA_PATH`. Si no existe, crea uno con valores por defecto. Es utilizada por `load_schema` cuando el parámetro `ensure=True`.

## Flujo interno

1. Verifica si `SCHEMA_PATH` existe.
2. Si no existe:
   - Crea los directorios padre necesarios.
   - Escribe un esquema por defecto (`DEFAULT_SCHEMA`) en formato YAML.
   - Registra un mensaje informativo.
3. Si existe, no realiza ninguna acción.

## Entradas y salidas

- **Entradas:** Ninguna (usa la constante `SCHEMA_PATH` del módulo `config`).
- **Salidas:** Crea o modifica el archivo `schema.yml` en el sistema de archivos.

## Efectos secundarios

- Escritura en disco del archivo de esquema.
- Logging de advertencias e información.

## Notas de mantenimiento

- El esquema por defecto se define como un diccionario estático `DEFAULT_SCHEMA` al inicio del módulo. Si se añaden nuevas secciones o audiencias, debe actualizarse este diccionario.
- La función es idempotente: si el archivo ya existe, no lo sobrescribe.

## Símbolos relacionados

- `load_schema` (pública) – función que invoca a `_ensure_schema`.
- `src.config.SCHEMA_PATH` – ruta configurada para el esquema.
