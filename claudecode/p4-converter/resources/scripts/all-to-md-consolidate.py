#!/usr/bin/env python3
"""
alias: all-to-md-consolidate
version: 1.0
purpose: Consolida los chunks .tmp.md de un documento en un único Markdown final
created: 2026-02-24
last_updated: 2026-06-05
plugin: p4-converter
skill: any-to-md (Step 7)
"""

"""
Consolida los ficheros .tmp.md generados en el Step 6 (extracción LLM) en un único
documento Markdown final con frontmatter completo.

Uso:
    python3 all-to-md-consolidate.py \\
      --source <ruta/nombre.docx> \\
      --pdf    <ruta/nombre.pdf> \\
      --output <ruta/nombre.md>

Parámetros:
  --source  Fichero origen (para metadatos del frontmatter)
  --pdf     PDF de referencia para contar páginas y localizar los chunks .tmp.md
            (los chunks siempre están en la misma carpeta que este fichero)
  --output  Ruta del .md final (puede estar en una carpeta diferente al source)

Ejemplos:
    # Desde DOCX (output en la misma carpeta que el source)
    python3 all-to-md-consolidate.py \\
      --source input/docs/manual.docx \\
      --pdf    input/docs/manual.pdf \\
      --output input/docs/manual.md

    # Desde DOCX (output en carpeta diferente — OUTPUT_PATH configurado)
    python3 all-to-md-consolidate.py \\
      --source input/docs/manual.docx \\
      --pdf    input/docs/manual.pdf \\
      --output output/converted/manual.md

    # Desde PDF nativo (--source y --pdf apuntan al mismo fichero)
    python3 all-to-md-consolidate.py \\
      --source input/docs/guia.pdf \\
      --pdf    input/docs/guia.pdf \\
      --output input/docs/guia.md

Nota: los chunks .tmp.md se buscan SIEMPRE en la carpeta del --pdf (SOURCE_FOLDER),
no en la carpeta del --output. El script de consolidación es llamado desde
/p4-converter:any-to-md Step 7.
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Formatos que requieren conversión intermedia a PDF
FORMATS_VIA_PDF = {".doc", ".docx", ".ppt", ".pptx"}


def get_pdf_page_count(pdf_path: Path) -> int:
    """Obtiene el número de páginas del PDF usando qpdf."""
    try:
        result = subprocess.run(
            ["qpdf", "--show-npages", str(pdf_path)],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return 0


def find_chunks(pdf_path: Path) -> list[Path]:
    """
    Localiza todos los .tmp.md del documento en la misma carpeta, ordenados por rango de páginas.
    El prefijo se extrae del nombre del PDF (sin extensión).
    Patrón esperado: {nombre}_{001-005}.tmp.md
    """
    folder = pdf_path.parent
    stem = pdf_path.stem
    pattern = re.compile(rf"^{re.escape(stem)}_(\d{{3}})-(\d{{3}})\.tmp\.md$")

    chunks = []
    for f in folder.iterdir():
        if f.is_file() and pattern.match(f.name):
            m = pattern.match(f.name)
            page_from = int(m.group(1))
            chunks.append((page_from, f))

    chunks.sort(key=lambda x: x[0])
    return [f for _, f in chunks]


def strip_frontmatter(content: str) -> str:
    """Elimina el frontmatter YAML si el contenido lo tiene."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


def remove_redundant_chunk_headers(content: str) -> str:
    """
    Elimina encabezados de chunk artificiales del tipo:
    '# Documento (Páginas X-Y)' o '## Chunk X'
    """
    lines = content.split("\n")
    filtered = []
    chunk_header = re.compile(
        r"^#+\s+(.*[Pp]áginas?\s+\d+-\d+.*|[Cc]hunk\s+\d+.*|[Pp]arte\s+\d+.*)",
        re.IGNORECASE
    )
    for line in lines:
        if chunk_header.match(line):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def unify_section_hierarchy(content: str) -> str:
    """
    Asegura jerarquía coherente. Si no hay H1, promueve el primer H2 a H1.
    """
    lines = content.split("\n")
    has_h1 = any(line.startswith("# ") and not line.startswith("## ") for line in lines)

    if has_h1:
        return content

    promoted = []
    for line in lines:
        if line.startswith("## "):
            promoted.append("# " + line[3:])
        elif line.startswith("### "):
            promoted.append("## " + line[4:])
        elif line.startswith("#### "):
            promoted.append("### " + line[5:])
        else:
            promoted.append(line)
    return "\n".join(promoted)


def build_frontmatter(
    source_path: Path,
    pages: int,
    chunks: int,
    converted_via_pdf: bool
) -> str:
    """Genera el frontmatter YAML para el documento final."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ext = source_path.suffix.lstrip(".")
    via_pdf = str(converted_via_pdf).lower()
    return (
        "---\n"
        f"source: {source_path.name}\n"
        f"source_format: {ext}\n"
        f"converted_via_pdf: {via_pdf}\n"
        f"converted: {timestamp}\n"
        f"pages: {pages}\n"
        f"chunks: {chunks}\n"
        f"chunk_size: 5\n"
        f"split_tool: qpdf\n"
        "---\n\n"
    )


def consolidate(source_path: Path, pdf_path: Path, output_path: Path) -> None:
    """Proceso principal de consolidación."""

    converted_via_pdf = source_path.suffix.lower() in FORMATS_VIA_PDF

    # 1. Localizar chunks (usando el stem del PDF como prefijo)
    chunks = find_chunks(pdf_path)
    if not chunks:
        print(f"ERROR: No se encontraron ficheros .tmp.md para '{pdf_path.stem}'", file=sys.stderr)
        print(f"       Buscando en: {pdf_path.parent}", file=sys.stderr)
        sys.exit(1)

    print(f"Chunks encontrados: {len(chunks)}")
    for c in chunks:
        print(f"  - {c.name}")

    # 2. Leer y procesar cada chunk
    sections = []
    for chunk_path in chunks:
        raw = chunk_path.read_text(encoding="utf-8")
        content = strip_frontmatter(raw)
        content = remove_redundant_chunk_headers(content)
        content = content.strip()
        if content:
            sections.append(content)

    if not sections:
        print("ERROR: Todos los chunks están vacíos. No se puede consolidar.", file=sys.stderr)
        sys.exit(1)

    # 3. Unir secciones
    merged = "\n\n".join(sections)
    merged = unify_section_hierarchy(merged)

    # 4. Obtener metadatos
    pages = get_pdf_page_count(pdf_path)
    if pages == 0:
        last_chunk = chunks[-1].name
        m = re.search(r"_(\d+)-(\d+)\.tmp\.md$", last_chunk)
        if m:
            pages = int(m.group(2))

    # 5. Generar frontmatter y escribir
    frontmatter = build_frontmatter(source_path, pages, len(chunks), converted_via_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(frontmatter + merged + "\n", encoding="utf-8")

    print(f"\n══════════════════════════════════════════")
    print(f"  CONSOLIDACIÓN COMPLETADA")
    print(f"══════════════════════════════════════════")
    print(f"  Documento:    {output_path.name}")
    print(f"  Origen:       {source_path.name}")
    print(f"  Páginas:      {pages}")
    print(f"  Chunks:       {len(chunks)} (.tmp.md fusionados)")
    print(f"══════════════════════════════════════════")
    print(f"\nSiguiente paso: /p4-converter:any-to-md Step 8 (revisión y limpieza)")
    print(f"  Limpieza de temporales (el PDF se conserva):")
    print(f"    rm {pdf_path.parent}/{pdf_path.stem}_*.tmp.pdf")
    print(f"    rm {pdf_path.parent}/{pdf_path.stem}_*.tmp.md")


def main():
    parser = argparse.ArgumentParser(
        description="Consolida chunks .tmp.md en un documento Markdown final."
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Fichero origen (ej: input/docs/manual.docx o input/docs/guia.pdf)"
    )
    parser.add_argument(
        "--pdf",
        required=True,
        type=Path,
        help="PDF de referencia para contar páginas (ej: input/docs/manual.pdf)"
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Ruta del fichero Markdown de salida (ej: input/docs/manual.md)"
    )
    args = parser.parse_args()

    source_path = args.source.resolve()
    pdf_path = args.pdf.resolve()
    output_path = args.output.resolve()

    if not source_path.exists():
        print(f"ERROR: El fichero origen no existe: {source_path}", file=sys.stderr)
        sys.exit(1)

    if not pdf_path.exists():
        print(f"ERROR: El PDF de referencia no existe: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    consolidate(source_path, pdf_path, output_path)


if __name__ == "__main__":
    main()
