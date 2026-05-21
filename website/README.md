# Sitio de documentacion

Esta carpeta contiene un sitio Docusaurus separado del codigo de negocio. El contenido fuente vive en `../docs` y el sitio se sirve desde esta carpeta.

## Requisitos

- Node.js 18 o superior
- npm

## Instalacion

```bash
cd website
npm install
```

## Desarrollo local

```bash
cd website
npm start
```

Antes de arrancar o compilar, el script `python -m src.docs_site_sync` actualiza la home global y los indices navegables dentro de `../docs`.

## Build de produccion

```bash
cd website
npm run build
```
