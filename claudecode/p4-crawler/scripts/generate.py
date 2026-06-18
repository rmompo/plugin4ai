#!/usr/bin/env python3
# ---
# version: 2.3
# description: Generación de INDEX.md con estructura completa — COMMAND-GENERATE
# agent: doc-scrapper
# author: rmompo@gmail.com
# created: 2026-02-24T00:00:00
# updated: 2026-03-09T00:00:00
# ---
#
# Estructura del INDEX.md generado:
#   ## Parámetros de extracción  (sin numerar)
#   ## Índice                    (sin numerar)
#   ## 1. Páginas
#   ### 1.1 {Página 1}
#       - descripción, adjuntos, [↑ índice]
#   ### 1.2 {Página 2} ...
#   ## 2. Ficheros generados
#   ## 3. Métricas del proceso
#
# Requiere que COMMAND-6-DOWNLOAD haya ejecutado antes:
#   - downloads/pages/*.md   (contenido de páginas, sin links)
#   - downloads/files/*      (ficheros adjuntos)
#   - data/file-url-map.json (mapa url → nombre local de adjunto)

import json, datetime, os, re, sys

DEFAULT_CONFIG    = "generated/scrapp/mova3/data/scrapper-config.json"
CONFIG_PATH       = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG

with open(CONFIG_PATH, encoding='utf-8') as _f:
    _cfg = json.load(_f)

_folder           = _cfg["output"]["folder"]
_data             = os.path.join(_folder, "data")
FILTERED_PATH     = os.path.join(_data, "web-map-filtered.jsonl")
EXCLUDED_PATH     = os.path.join(_data, "web-map-excluded.jsonl")
FILE_URL_MAP_PATH = os.path.join(_data, "file-url-map.json")
PAGE_DESCS_PATH   = os.path.join(_data, "page-descriptions.json")
SESSION_TMP       = os.path.join(_data, "scrapper-session.tmp")
OUTPUT_PATH       = os.path.join(_folder, "INDEX.md")
PAGES_DIR         = os.path.join(_folder, "downloads", "pages")
FILES_DIR         = os.path.join(_folder, "downloads", "files")
IMAGES_DIR        = os.path.join(_folder, "downloads", "images")

print(f"\n{'═'*60}")
print(f"  COMMAND-5-GENERATE v2.0 — Generación de INDEX.md")
print(f"{'═'*60}\n")

# ── Fase 0: Eliminar credenciales si existen ──────────────────────────────────
if os.path.exists(SESSION_TMP):
    os.remove(SESSION_TMP)
    print("  scrapper-session.tmp eliminado ✓")

# ── Fase 1: Cargar datos ──────────────────────────────────────────────────────
config = _cfg

nodes_filtered, seen_names = [], set()
with open(FILTERED_PATH, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        n = json.loads(line)
        if n['type'] == 'file':
            key = re.sub(r'[^a-z0-9]', '', (n.get('title') or n['id']).lower())
            if key in seen_names: continue
            seen_names.add(key)
        nodes_filtered.append(n)

excl_reasons = {}
if os.path.exists(EXCLUDED_PATH):
    with open(EXCLUDED_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                r = json.loads(line)
                reason = r.get('excluded_reason', 'unknown')
                excl_reasons[reason] = excl_reasons.get(reason, 0) + 1
            except Exception:
                pass

# Cargar file-url-map (url → nombre local de fichero)
file_url_map = {}
if os.path.exists(FILE_URL_MAP_PATH):
    with open(FILE_URL_MAP_PATH, encoding='utf-8') as f:
        file_url_map = json.load(f)

# Cargar descripciones pre-generadas por el agente (clave = node id)
page_descs = {}
if os.path.exists(PAGE_DESCS_PATH):
    with open(PAGE_DESCS_PATH, encoding='utf-8') as f:
        page_descs = json.load(f)

pages = [n for n in nodes_filtered if n['type'] == 'page']
files = [n for n in nodes_filtered if n['type'] == 'file']

print(f"  Páginas: {len(pages)}  |  Ficheros: {len(files)}")

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(text):
    text = (text or '').lower().strip()
    for s, d in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        text = text.replace(s, d)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50].strip('-')

def anchor(text):
    """Genera anchor compatible con GitHub Flavored Markdown.
    GFM: lowercase, elimina todo excepto letras/dígitos/espacios/guiones, espacios→guiones.
    A diferencia de slugify(), conserva caracteres acentuados (á, é, ñ…).
    """
    text = (text or '').lower().strip()
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def page_fname(node):
    return f"{node['id']}-{slugify(node.get('title', node['id']))}.md"

def file_size_bytes(fname):
    path = os.path.join(FILES_DIR, fname)
    return os.path.getsize(path) if os.path.exists(path) else 0

def file_size_str(fname):
    size = file_size_bytes(fname)
    if not size: return ''
    if size >= 1_000_000: return f'{size/1_000_000:.1f} MB'
    if size >= 1_000:     return f'{size/1_000:.0f} KB'
    return f'{size} B'

def reduction_factor(orig_fname, md_fname):
    orig = file_size_bytes(orig_fname)
    md   = file_size_bytes(md_fname)
    if not orig or not md: return '—'
    ratio = orig / md
    return f'{ratio:.0f}x'

def read_page_content(fname):
    """Lee el .md descargado, elimina cabecera y limpia artefactos de conversión."""
    path = os.path.join(PAGES_DIR, fname)
    if not os.path.exists(path):
        return ''
    with open(path, encoding='utf-8') as f:
        content = f.read()
    # Eliminar cabecera hasta el primer "---\n\n"
    content = re.sub(r'^.*?---\n\n', '', content, count=1, flags=re.DOTALL)
    # Eliminar líneas con imágenes apuntando a ficheros (iconos de descarga)
    content = re.sub(r'!\[[^\]]*\]\(\.\./files/[^\)]+\)', '', content)
    # Eliminar líneas con "!texto" (fa-robot u otros iconos sin href)
    content = re.sub(r'^![^[\n]+$', '', content, flags=re.MULTILINE)
    # Limpiar líneas vacías múltiples
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()

def generate_description(title, content):
    """Genera descripción breve a partir del contenido de la página.

    Extrae las primeras frases significativas y las combina en un párrafo
    que explica qué es la página y qué información contiene.
    """
    def fix_enc(s):
        """Corrige double-encoding UTF-8 bytes interpretados como Latin-1 o MacRoman.

        Casos:
          - Latin-1: Ã³ (c3 83 c2 b3) → ó  (c3 b3)
          - MacRoman: √≥ (e2 88 9a e2 89 a5) → ó  (c3 b3)
        """
        # Intento 1: Latin-1 → UTF-8 (ej: Ã³ → ó)
        try:
            return s.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        # Intento 2: MacRoman → UTF-8 (ej: √≥ → ó)
        try:
            return s.encode('mac_roman').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        return s

    # Recoger líneas de texto con contenido real (no encabezados vacíos, no separadores)
    sentences = []
    for line in content.split('\n'):
        line = fix_enc(line)
        line = re.sub(r'^#+\s*', '', line).strip()          # quitar marcas de heading
        line = re.sub(r'\*+', '', line).strip()              # quitar negrita/cursiva
        line = re.sub(r'[`_~]', '', line).strip()            # quitar otros marcadores
        line = re.sub(r':::[\w]*\s*', '', line).strip()      # quitar callouts MDX (:::warning, :::)
        line = re.sub(r'<[^>]+>', '', line).strip()          # quitar tags HTML inline
        line = re.sub(r'\\+$', '', line).strip()             # quitar backslashes finales (line breaks MD)
        line = re.sub(r'[\ue000-\uf8ff\ufff0-\uffff]', '', line).strip()  # quitar PUA / icon fonts
        if not line or line in ('---', '* * *', '***'): continue
        if line.startswith(('!', '|', '>')): continue
        if line.count('|') >= 2: continue   # filas de tabla (con | en medio)
        if len(line) < 8: continue
        sentences.append(line)
        if len(' '.join(sentences)) > 400:
            break
    desc = ' '.join(sentences[:6])
    if len(desc) > 350:
        desc = desc[:347] + '…'
    return desc or title

def get_page_adjuntos(page_node):
    """Devuelve lista de adjuntos {name, local_file, size} para una página."""
    adjuntos = []
    seen_urls = set()
    for att in page_node.get('attachments', []):
        url  = att.get('url', '')  if isinstance(att, dict) else str(att)
        name = att.get('name', '') if isinstance(att, dict) else ''
        if not url or url in seen_urls: continue
        seen_urls.add(url)
        local = file_url_map.get(url)
        if not local:
            # Buscar por ID de fichero en la lista
            fnode = next((f for f in files if f['url'] == url), None)
            if fnode:
                local = f"{fnode['id']}-{slugify(fnode.get('title', fnode['id']))}.bin"
        if not name:
            name = (local or url).split('/')[-1]
        adjuntos.append({'name': name, 'local': local, 'url': url})
    return adjuntos

# ── Fase 2: Generar INDEX.md ──────────────────────────────────────────────────
cfg_crawl  = config.get('crawl', {})
cfg_filter = config.get('filter', {})
cfg_out    = config.get('output', {})
cfg_met    = config.get('metrics', {})
now_str    = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

keywords_str = ', '.join(f'`{k}`' for k in cfg_filter.get('keywords', []))
folder       = cfg_out.get('folder', 'generated/scrapp/mova3')

lines = []

# ══════════════════════════════════════════════════════════
# Título
# ══════════════════════════════════════════════════════════
lines += [
    "# Documentación MOVA 3 — Extracción de Normativa",
    "",
    f"> Generado: {now_str}",
    "",
    "---",
    "",
]

# ══════════════════════════════════════════════════════════
# 1. Parámetros de extracción
# ══════════════════════════════════════════════════════════
lines += [
    "## Parámetros de extracción",
    "",
    "| Parámetro | Valor |",
    "|-----------|-------|",
    f"| Tópico | {cfg_filter.get('topic', '—')} |",
    f"| Keywords | {keywords_str} |",
    f"| URL de inicio | {cfg_crawl.get('start_url', '—')} |",
    f"| Carpeta de salida | `{folder}` |",
    f"| Agente | doc-scrapper v2.0 |",
    "",
    "---",
    "",
]

# ══════════════════════════════════════════════════════════
# 2. Índice
# ══════════════════════════════════════════════════════════
lines += ['<a name="indice"></a>', "", "## Índice", ""]
lines.append("- [1. Páginas](#s1)")
for i, n in enumerate(pages, 1):
    title = n.get('title', n['id'])
    lines.append(f"  - [1.{i} {title}](#s1-{i})")
lines += [
    "- [2. Ficheros generados](#s2)",
    "- [3. Métricas del proceso](#s3)",
    "", "---", "",
]

idx_anchor = "indice"   # anchor del tag <a name="indice"></a>

def adj_label(a):
    if not a['local']:
        return a['name']
    ext  = os.path.splitext(a['local'])[1]
    name = a['name']
    return name if name.lower().endswith(ext.lower()) else name + ext

def build_adj_table(adjuntos, files_prefix):
    """Construye tabla Markdown de adjuntos. files_prefix: ruta relativa a la carpeta files/."""
    if not adjuntos:
        return []
    rows = []
    for a in adjuntos:
        if not a['local']:
            rows.append(f"| {a['name']} *(no descargado)* | — | — |")
            continue
        label     = adj_label(a)
        size      = file_size_str(a['local'])
        size_part = f' ({size})' if size else ''
        orig_cell = f"[{label}]({files_prefix}{a['local']}){size_part}"
        md_local  = os.path.splitext(a['local'])[0] + '.md'
        md_full   = os.path.join(FILES_DIR, md_local)
        if os.path.exists(md_full):
            md_size      = file_size_str(md_local)
            md_size_part = f' ({md_size})' if md_size else ''
            md_label     = os.path.splitext(label)[0] + '.md'
            md_cell      = f"[{md_label}]({files_prefix}{md_local}){md_size_part}"
            red_cell     = reduction_factor(a['local'], md_local)
        else:
            md_cell  = '—'
            red_cell = '—'
        rows.append(f"| {orig_cell} | {md_cell} | {red_cell} |")
    return [
        "**Adjuntos:**", "",
        "| Original | Markdown | Reducción |",
        "|----------|----------|-----------|",
    ] + rows

# Sección 1. Páginas
lines += ['<a name="s1"></a>', "", "## 1. Páginas", ""]

for i, n in enumerate(pages, 1):
    title    = n.get('title', n['id'])
    fname    = page_fname(n)
    content  = read_page_content(fname)
    adjuntos = get_page_adjuntos(n)
    desc     = page_descs.get(n['id']) or generate_description(title, content)

    adj_section = build_adj_table(adjuntos, files_prefix='downloads/files/')

    lines += [
        f"<a name=\"s1-{i}\"></a>",
        "",
        f"### 1.{i} {title} — [ver](downloads/pages/{fname})",
        "",
        desc,
    ] + ([""] + adj_section if adj_section else []) + [
        "",
        f"[↑ Volver al índice](#{idx_anchor})",
        "",
        "---",
        "",
    ]

    # Actualizar el .md de la página: back-link + tabla de adjuntos
    page_path = os.path.join(PAGES_DIR, fname)
    if os.path.exists(page_path):
        with open(page_path, encoding='utf-8') as f:
            page_src = f.read()

        # 1) Eliminar título (# Heading de primer nivel) y back-link
        page_src = re.sub(r'^#[^\n]+\n+', '', page_src)
        page_src = re.sub(r'\[←[^\]]*\]\([^)]*\)\n*', '', page_src)

        # 2) Convertir ![](../files/xxx)Texto → [Texto](../files/xxx) en contenido inline
        def _file_img_to_link(m):
            rel_path   = m.group(1)
            text       = m.group(2).strip()
            local_name = rel_path.split('/')[-1]
            if os.path.exists(os.path.join(FILES_DIR, local_name)):
                label = text if text else local_name
                return f'[{label}]({rel_path})'
            return text

        page_src = re.sub(
            r'!\[[^\]]*\]\((\.\./files/[^\)]+)\)([^\n]*)',
            _file_img_to_link,
            page_src
        )

        # 3) Normalizar cabecera: tabla Aspecto|Valor o línea Fuente ya procesada → "Fuente: {link}\n\n---\n\n"
        def _replace_header_table(m):
            fuente_match = re.search(r'\| Fuente \| (.+?) \|', m.group(0))
            fuente = fuente_match.group(1).strip() if fuente_match else ''
            # Extraer URL plain de un posible link Markdown [url](url)
            fuente = re.sub(r'^\[([^\]]+)\]\([^)]+\)$', r'\1', fuente)
            return f"Fuente: {fuente}\n\n---\n\n" if fuente else '---\n\n'
        page_src = re.sub(
            r'\| Aspecto \| Valor \|.*?\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)*',
            _replace_header_table,
            page_src,
            flags=re.DOTALL
        )
        # Normalizar "**Fuente:**" o "Fuente:" ya existente → "Fuente: {valor}\n\n---\n\n"
        page_src = re.sub(r'\*\*Fuente:\*\*\s*', 'Fuente: ', page_src)
        # Extraer URL plain si tiene formato Markdown link
        page_src = re.sub(r'(Fuente: )\[([^\]]+)\]\([^)]+\)', r'\1\2', page_src)
        page_src = re.sub(r'(Fuente:[^\n]+)\n+(?:---\n+)?', r'\1\n\n---\n\n', page_src)

        # 4) Limpiar cualquier tabla de adjuntos previa insertada por runs anteriores
        page_src = re.sub(
            r'\n*\*\*Adjuntos:\*\*\n\n\|[^\n]+\|\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)*',
            '',
            page_src,
            flags=re.DOTALL
        )

        # 5) En el contenido: limpiar sufijos "&#124; [Markdown/Markdown format](...)"
        page_src = re.sub(
            r' &#124; \[[^\]]*\]\(\.\./files/[^\)]+\.md\)',
            '',
            page_src
        )

        # 6) En el contenido: redirigir links a ficheros originales → versión .md si existe
        def _redirect_to_md(m):
            text       = m.group(1)
            rel_path   = m.group(2)   # ../files/n547-xxx.pdf
            local_name = rel_path.split('/')[-1]
            md_name    = os.path.splitext(local_name)[0] + '.md'
            md_full    = os.path.join(FILES_DIR, md_name)
            if os.path.exists(md_full):
                return f'[{text}](../files/{md_name})'
            return m.group(0)

        page_src = re.sub(
            r'\[([^\]]+)\]\((\.\./files/[^\)]+)\)',
            _redirect_to_md,
            page_src
        )

        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page_src)
        print(f"  página actualizada: {fname}")

# ══════════════════════════════════════════════════════════
# 3b. Actualizar ficheros .md en downloads/files/ con cabecera Fuente + ---
# ══════════════════════════════════════════════════════════
# Invertir file_url_map: local_filename → url_original
local_to_url = {v: k for k, v in file_url_map.items()}

if os.path.exists(FILES_DIR):
    for md_fname in os.listdir(FILES_DIR):
        if not md_fname.endswith('.md'):
            continue
        md_path = os.path.join(FILES_DIR, md_fname)
        with open(md_path, encoding='utf-8') as f:
            content = f.read()

        # Determinar URL original: buscar el fichero original (mismo nombre sin .md + cualquier extensión)
        base = os.path.splitext(md_fname)[0]   # ej. n547-28570-mova3-framework-presentacion-1
        orig_url = None
        for local, url in local_to_url.items():
            if os.path.splitext(local)[0] == base:
                orig_url = url
                break

        # Limpiar cabecera previa y cualquier --- inicial del contenido
        content = re.sub(r'^Fuente:[^\n]*\n+---\n+', '', content)
        content = re.sub(r'^(---\n+)+', '', content)
        # Eliminar bloque de metadatos all-to-md (source:, source_format:, pages:, etc.)
        content = re.sub(r'^(?:source|source_format|converted_via_pdf|converted|pages|chunks|chunk_size|split_tool):[^\n]*\n', '', content, flags=re.MULTILINE)
        # Eliminar secciones de Índice y Registro de Cambios (cualquier nivel de heading)
        content = re.sub(r'#{1,6}\s*(índice|indice|tabla de contenido|registro de cambios|historial de cambios|changelog)[^\n]*\n.*?(?=\n#{1,6}\s|\Z)', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = content.lstrip('\n')

        # Insertar cabecera
        if orig_url:
            header = f"Fuente: {orig_url}\n\n---\n\n"
        else:
            header = ''

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(header + content)

    print(f"  ficheros .md actualizados con cabecera Fuente")

# ══════════════════════════════════════════════════════════
# 4. Ficheros generados
# ══════════════════════════════════════════════════════════
img_count = len(os.listdir(IMAGES_DIR)) if os.path.exists(IMAGES_DIR) else 0
lines += [
    '<a name="s2"></a>',
    "",
    "## 2. Ficheros generados",
    "",
    "```",
    f"{folder}/",
    f"├── INDEX.md",
    f"├── data/",
    f"│   ├── scrapper-config.json",
    f"│   ├── web-map-nodes.jsonl",
    f"│   ├── web-map-filtered.jsonl",
    f"│   ├── web-map-excluded.jsonl",
    f"│   └── file-url-map.json",
    f"└── downloads/",
    f"    ├── pages/",
]
for n in pages:
    lines.append(f"    │   └── {page_fname(n)}")
lines.append(f"    ├── files/")
for n in files:
    local = file_url_map.get(n['url'], f"{n['id']}-{slugify(n.get('title', n['id']))}.bin")
    lines.append(f"    │   └── {local}")
lines.append(f"    └── images/")
lines.append(f"        └── ({img_count} imágenes)")
lines += ["```", "", f"[↑ Volver al índice](#{idx_anchor})", "", "---", ""]

# ══════════════════════════════════════════════════════════
# 3. Métricas del proceso
# ══════════════════════════════════════════════════════════
total_excl = sum(excl_reasons.values())
lines += [
    '<a name="s3"></a>',
    "",
    "## 3. Métricas del proceso",
    "",
    "| Métrica | Valor |",
    "|---------|-------|",
    f"| Páginas incluidas | {len(pages)} |",
    f"| Ficheros adjuntos | {len(files)} |",
    f"| Imágenes descargadas | {img_count} |",
    f"| Páginas excluidas (total) | {total_excl} |",
    f"| · Sin keywords del tópico | {excl_reasons.get('filter_topic', 0)} |",
    f"| · Patrones ignorados (pre-filtro URL) | {excl_reasons.get('ignored_pattern', 0)} |",
    f"| · Duplicados por hash | {excl_reasons.get('duplicate_content', 0)} |",
    f"| · Errores de descarga | {excl_reasons.get('fetch_error', 0)} |",
    f"| Total nodos crawleados | {cfg_met.get('nodes_total', '—')} |",
    f"| Peticiones HTTP crawl | {cfg_met.get('http_requests', '—')} |",
    f"| Duración crawl | {cfg_met.get('crawl_duration_s', '—')} s |",
    f"| Fecha generación | {now_str} |",
    "",
    f"[↑ Volver al índice](#{idx_anchor})",
]

# ── Escribir INDEX.md ─────────────────────────────────────────────────────────
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

# ── Actualizar config ─────────────────────────────────────────────────────────
now_ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
config.setdefault('session', {})['generate_status']    = 'ok'
config.setdefault('session', {})['generate_timestamp'] = now_ts
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"\n{'═'*60}")
print(f"  INDEX.md GENERADO")
print(f"{'═'*60}")
print(f"  Fichero: {OUTPUT_PATH}")
print(f"  Páginas: {len(pages)}  |  Adjuntos: {len(files)}  |  Imágenes: {img_count}")
print(f"{'═'*60}\n")
