"""Synchronize navigable index pages for static documentation sites.

This module maintains landing pages under ``docs/`` so the generated markdown
is usable both in-repo and in site generators such as Docusaurus.

Project implications:
- Documentation quality in this project is not only about content, but also
  about browseability for reviewers and end users.
- Generated landing pages create a second layer of derived docs that must stay
  consistent with the primary markdown pages.
- Because these pages may also be indexed into the vector store, navigation and
  retrieval behavior are indirectly connected.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


DOCS_ROOT = Path.cwd() / "docs"
MANAGED_MARKER = "<!-- AUTO-GENERATED: docs-site-sync -->"
SKIP_FILES = {"schema.yml"}
INDEX_CANDIDATES = ("index.md", "README.md")


def _title_from_dir(directory: Path) -> str:
    relative = directory.relative_to(DOCS_ROOT)
    if relative == Path("."):
        return "Inicio"

    mapping = {
        "dev": "Documentacion para desarrolladores",
        "user": "Documentacion para usuarios",
        "reference": "Referencia",
        "public": "API publica",
        "internal": "API interna",
        "modules": "Modulos",
        "classes": "Clases",
        "functions": "Funciones",
        "how-to": "Guias practicas",
        "tutorials": "Tutoriales",
        "explanation": "Explicaciones",
    }
    name = directory.name
    return mapping.get(name, name.replace("-", " ").replace("_", " ").title())


def _description_from_dir(directory: Path) -> str:
    relative = directory.relative_to(DOCS_ROOT)
    if relative == Path("."):
        return "Portal principal de la documentacion del proyecto."
    return f"Indice navegable de la seccion {' / '.join(relative.parts)}."


def _index_filename_for(directory: Path) -> str:
    for candidate in INDEX_CANDIDATES:
        if (directory / candidate).exists():
            return candidate
    return "index.md"


def _managed_index_path(directory: Path) -> Path:
    return directory / _index_filename_for(directory)


def _child_directories(directory: Path) -> list[Path]:
    return sorted(
        [
            child
            for child in directory.iterdir()
            if child.is_dir() and not child.name.startswith(".")
        ],
        key=lambda path: path.name.lower(),
    )


def _child_markdown_files(directory: Path, index_path: Path) -> list[Path]:
    return sorted(
        [
            child
            for child in directory.iterdir()
            if child.is_file()
            and child.suffix.lower() in {".md", ".mdx"}
            and child.name not in SKIP_FILES
            and child != index_path
            and child.name.lower() not in {"readme.md", "index.md"}
        ],
        key=lambda path: path.name.lower(),
    )


def _relative_link(from_dir: Path, to_path: Path) -> str:
    relative = to_path.relative_to(from_dir)
    return relative.as_posix()


def _build_frontmatter(directory: Path) -> str:
    title = _title_from_dir(directory)
    description = _description_from_dir(directory)
    lines = [
        "---",
        f"title: {title}",
        f"sidebar_label: {title}",
        f"description: {description}",
        "sidebar_position: 1",
    ]
    if directory == DOCS_ROOT:
        lines.append("slug: /")
    lines.append("---")
    return "\n".join(lines)


def _build_section(title: str, items: Iterable[str]) -> str:
    items = list(items)
    if not items:
        return f"## {title}\n\n- Sin elementos aún."
    return f"## {title}\n\n" + "\n".join(items)


def build_index_content(directory: Path) -> str:
    index_path = _managed_index_path(directory)
    child_dirs = _child_directories(directory)
    child_docs = _child_markdown_files(directory, index_path)

    section_items = [
        f"- [{_title_from_dir(child)}]({_relative_link(directory, _managed_index_path(child))})"
        for child in child_dirs
    ]
    doc_items = [
        f"- [{doc.stem.replace('-', ' ').replace('_', ' ').title()}]({_relative_link(directory, doc)})"
        for doc in child_docs
    ]

    overview = (
        "Esta pagina se actualiza automaticamente para servir como punto de entrada "
        "navegable en el sitio de documentacion."
    )

    content_parts = [
        _build_frontmatter(directory),
        "",
        MANAGED_MARKER,
        "",
        f"# {_title_from_dir(directory)}",
        "",
        overview,
        "",
        _build_section("Subsecciones", section_items),
        "",
        _build_section("Documentos", doc_items),
        "",
    ]
    return "\n".join(content_parts)


def sync_docs_site_indexes() -> list[Path]:
    """Generate or refresh managed landing pages under docs/."""
    if not DOCS_ROOT.exists():
        return []

    updated_paths: list[Path] = []
    directories = sorted(
        [DOCS_ROOT, *[path for path in DOCS_ROOT.rglob("*") if path.is_dir()]],
        key=lambda path: (len(path.parts), str(path).lower()),
    )

    for directory in directories:
        index_path = _managed_index_path(directory)
        content = build_index_content(directory)
        should_write = True

        if index_path.exists():
            existing = index_path.read_text(encoding="utf-8")
            should_write = existing.startswith(MANAGED_MARKER) or existing != content

        if should_write:
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(content, encoding="utf-8")
            updated_paths.append(index_path)
            print(f"[docs_site_sync] Updated index: {index_path}")

    return updated_paths


if __name__ == "__main__":
    updated = sync_docs_site_indexes()
    print(f"[docs_site_sync] Total index files updated: {len(updated)}")
