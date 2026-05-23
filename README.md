![IA Project Logo](assets/logo.png)

# Documentación Automática con IA + RAG

Pipeline de documentación automatizada que utiliza inteligencia artificial para generar, actualizar y mantener la documentación técnica de un proyecto de software de forma continua, integrado en un flujo CI/CD.

## Índice

- [Cómo funciona](#cómo-funciona)
- [Sistema RAG](#sistema-rag)
- [Esquema de documentación (schema.yml)](#esquema-de-documentación-schemayml)
- [Salida: sitio estático con Docusaurus](#salida-sitio-estático-con-docusaurus)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Adaptar el pipeline a tu proyecto](#adaptar-el-pipeline-a-tu-proyecto)

## Cómo funciona

Cada vez que se detectan cambios en el código fuente (`src/`) en la rama `master`, un workflow de GitHub Actions ejecuta el pipeline:

1. **Detección de cambios** — Se extrae el diff de git de los archivos modificados.
2. **Consulta RAG** — Se busca en un índice semántico (ChromaDB + LlamaIndex) la documentación existente relacionada con los cambios detectados, recuperando contexto relevante de docs anteriores.
3. **Decisión con LLM** — El diff y el contexto recuperado se envían a un modelo de lenguaje (DeepSeek) que decide qué archivos de documentación crear, actualizar o eliminar.
4. **Ejecución** — Se aplican las acciones decididas sobre los archivos Markdown en `docs/`.
5. **Publicación** — Los cambios se commitean en la rama `docs/ia` y se reflejan automáticamente en el sitio estático generado con Docusaurus.

## Sistema RAG

El núcleo del pipeline es un sistema de Retrieval-Augmented Generation (RAG) que indexa toda la documentación existente en un vector store. Antes de generar nueva documentación, consulta este índice para:

- Contrastar la documentación ya escrita contra los cambios actuales.
- Evitar duplicados y redundancias.
- Mantener consistencia tonal, estructural y terminológica con documentos anteriores.
- Proporcionar contexto relevante al LLM para que las decisiones sean informadas.

## Esquema de documentación (`schema.yml`)

El archivo `docs/schema.yml` define el estilo, estructura y reglas de documentación del proyecto. En él se especifican:

- Audiencias objetivo (desarrolladores y usuarios finales).
- Secciones requeridas (tutoriales, guías, referencia, explicaciones).
- Reglas de decisión sobre cuándo y cómo documentar según el tipo de cambio.
- Plantillas de frontmatter y contenido para cada tipo de página.
- Convenciones de nombrado, navegación y enlazado.

No exige un formato rígido: está diseñado para que la IA lo interprete de forma óptima y genere documentación coherente con las reglas definidas.

## Salida: sitio estático con Docusaurus

La documentación generada se publica como un sitio web estático construido con **Docusaurus**, con soporte completo para navegación lateral, búsqueda y organización por audiencias.

## Stack tecnológico

| Componente        | Tecnología                         |
|-------------------|------------------------------------|
| Pipeline          | Python                             |
| Orquestación CI   | GitHub Actions                     |
| Vector store (RAG)| ChromaDB                           |
| Indexado semántico| LlamaIndex + sentence-transformers |
| LLM               | DeepSeek (API)                     |
| Sitio de docs     | Docusaurus                         |
| Esquema           | YAML (`schema.yml`)                |

## Estructura del proyecto

```
.
├── .github/workflows/   # Workflow CI/CD (docs-pipeline.yml)
├── docs/                # Documentación generada
│   ├── dev/             #   Documentación para desarrolladores
│   ├── user/            #   Documentación para usuarios finales
│   └── schema.yml       #   Esquema de estilo y reglas
├── src/                 # Código fuente del pipeline
│   ├── generate_docs.py #   Orquestador principal
│   ├── diff_parser.py   #   Extracción de cambios git
│   ├── rag_manager.py   #   Indexado y consulta RAG
│   ├── llm_decider.py   #   Prompt y decisión con LLM
│   ├── docs_site_sync.py#   Sincronización de índices del sitio
│   └── config.py        #   Configuración centralizada
├── vector_store/        # Índice semántico persistente (ChromaDB)
├── website/             # Sitio Docusaurus
└── requirements.txt
```

## Adaptar el pipeline a tu proyecto

Puedes integrar este pipeline en cualquier repositorio de código siguiendo estos pasos:

1. **Copia los directorios `src/`, `vector_store/` y `website/`** a la raíz de tu proyecto.
2. **Copia el workflow** `.github/workflows/docs-pipeline.yml` a tu repositorio.
3. **Configura las variables de entorno** necesarias en los Secrets de tu repositorio (GitHub Actions → Secrets):
   - `DEEPSEEK_API_KEY` — Tu clave de API de DeepSeek.
4. **Personaliza `docs/schema.yml`** con las reglas de documentación de tu proyecto.
5. **Ajusta `src/config.py`** para que apunte a las rutas correctas de tu código fuente y directorio de documentación.

Una vez hecho esto, el pipeline se ejecutará automáticamente en cada push a `master` que modifique archivos en `src/`, generando y actualizando la documentación sin intervención manual.
