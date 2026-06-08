#!/usr/bin/env python3
# ---
# version: 3.4
# description: Descarga páginas como Markdown + adjuntos + imágenes, con expansión configurable — COMMAND-DOWNLOAD
# agent: doc-scrapper
# author: rmompo@gmail.com
# created: 2026-02-24T00:00:00
# updated: 2026-03-09T00:00:00
# ---
#
# Novedades v3.4:
#   - storybook_iframe_url(): convierte /?path=/docs/... → /iframe.html?viewMode=docs&id=...
#   - download_with_playwright() usa la URL del iframe directamente para Storybook
# Novedades v3.3:
#   - download.expand: false en config → salta Fase 1 (sin seguir links)
# Novedades v3.2:
#   - CONFIG_PATH desde sys.argv[1] (con fallback al path mova3)
#   - Paths derivados de config["output"]["folder"] en lugar de hardcodeados
#   - Verificación de sesión condicional a auth.login_required
#   - Fallback a web-map-nodes.jsonl si web-map-filtered.jsonl no existe
#   - Import condicional de Playwright (playwright.sync_api)
#   - download_with_playwright(): descarga páginas SPA con Chromium headless
#   - Fase 1: skip de nodos SPA (se descargan con Playwright en Fase 3)
#   - Fase 3: bifurcación por node.get('spa') → Playwright / curl
# Novedades v3.1:
#   - Páginas .md SIN links: html_to_markdown usa ignore_links=True.
#   - Guarda file_url_map en data/file-url-map.json para uso de COMMAND-5.
#   - Elimina la fase de actualización de INDEX.md (ahora la hace COMMAND-5).
# Novedades v3.0:
#   - Fase 1 (Expansión): analiza HTML de páginas semilla con keywords.
#   - fix: regex de limpieza CSS usa ^cls$ (exacto).

import json, os, re, subprocess, sys, datetime, hashlib, urllib.parse
from urllib.parse import urlparse as _urlparse
from bs4 import BeautifulSoup
import html2text

# ── Configuración ─────────────────────────────────────────────────────────────
CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "generated/scrapp/mova3/data/scrapper-config.json"

with open(CONFIG_PATH, encoding='utf-8') as _f:
    config = json.load(_f)

_output       = config["output"]["folder"]
_data_dir     = f"{_output}/data"
FILTERED_PATH = f"{_data_dir}/web-map-filtered.jsonl"
WEBMAP_PATH   = f"{_data_dir}/web-map-nodes.jsonl"
COOKIES_PATH  = f"{_data_dir}/scrapper-cookies.txt"
INDEX_PATH    = f"{_output}/INDEX.md"
SESSION_TMP   = f"{_data_dir}/scrapper-session.tmp"
PAGES_DIR     = f"{_output}/downloads/pages"
FILES_DIR     = f"{_output}/downloads/files"
IMAGES_DIR    = f"{_output}/downloads/images"

_parsed_base = _urlparse(config["crawl"]["start_url"])
BASE_DOMAIN  = f"{_parsed_base.scheme}://{_parsed_base.netloc}"

# SPA config
_spa_cfg          = config.get('spa', {})
SPA_WAIT_SELECTOR = _spa_cfg.get('wait_selector', '.sbdocs-wrapper')
SPA_TIMEOUT_MS    = _spa_cfg.get('wait_timeout_ms', 10000)

# Playwright (opcional)
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

print(f"\n{'═'*60}")
print(f"  COMMAND-6-DOWNLOAD v3.0 — Descarga de contenido")
print(f"{'═'*60}\n")

# ── Fase 0: Verificar sesión ──────────────────────────────────────────────────
def check_session():
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '10',
             '-b', COOKIES_PATH, f'{BASE_DOMAIN}/arquitecturasw/index.php'],
            capture_output=True, text=True, timeout=15
        )
        return 'logout' in r.stdout.lower()
    except Exception:
        return False

_login_required = config.get('auth', {}).get('login_required', True)
if _login_required:
    if not check_session():
        print("  [ERROR] Sesión expirada. Ejecutar COMMAND-LOGIN y relanzar.")
        sys.exit(1)
    print("  Sesión activa ✓")
else:
    print("  Sin autenticación requerida ✓")

# ── Cargar datos ──────────────────────────────────────────────────────────────
# Keywords para expansión (mismos que el filtro)
keywords = [k.lower() for k in config.get('filter', {}).get('keywords',
            config.get('keywords', []))]

# Páginas y ficheros semilla (del filtro; fallback a todos los nodos si no existe)
_source_path = FILTERED_PATH if os.path.exists(FILTERED_PATH) else WEBMAP_PATH
if not os.path.exists(FILTERED_PATH):
    print(f"  [INFO] web-map-filtered.jsonl no encontrado — usando {WEBMAP_PATH}")
nodes_all, seen_names = [], set()
with open(_source_path, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        n = json.loads(line)
        if n['type'] == 'file':
            key = re.sub(r'[^a-z0-9]', '', (n.get('title') or n['id']).lower())
            if key in seen_names: continue
            seen_names.add(key)
        nodes_all.append(n)

pages_seed = [n for n in nodes_all if n['type'] == 'page']
files      = [n for n in nodes_all if n['type'] == 'file']

# Cargar TODOS los nodos del web-map para resolución de URLs en expansión
url_to_node = {}  # url → node (solo páginas)
if os.path.exists(WEBMAP_PATH):
    with open(WEBMAP_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                n = json.loads(line)
                if n.get('type') == 'page' and n.get('url'):
                    url_to_node[n['url']] = n
            except Exception:
                pass

os.makedirs(PAGES_DIR,  exist_ok=True)
os.makedirs(FILES_DIR,  exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
print(f"  Páginas semilla: {len(pages_seed)} | Ficheros: {len(files)} | Web-map: {len(url_to_node)} páginas")

# ── Helpers ───────────────────────────────────────────────────────────────────
def slugify(text):
    text = (text or '').lower()
    for s, d in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        text = text.replace(s, d)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:50].strip('-')

def absolute_url(href, page_url):
    if not href or href.startswith(('mailto:','tel:','javascript:','#')):
        return None
    if href.startswith('http'):
        return href
    if href.startswith('//'):
        return 'https:' + href
    if href.startswith('/'):
        return BASE_DOMAIN + href
    base = page_url.rsplit('/', 1)[0]
    return base + '/' + href

def matches_keywords(node):
    """Devuelve True si el nodo es relevante según las keywords del filtro."""
    if not keywords:
        return False  # sin keywords configuradas no expandir
    text = ' '.join(filter(None, [
        node.get('title', ''), node.get('description', ''), node.get('url', '')
    ])).lower()
    return any(kw in text for kw in keywords)

def is_decorative_img(tag):
    cls = ' '.join(tag.get('class', []))
    return bool(re.search(r'icon|logo|avatar|emoji|bullet|badge|spinner', cls, re.I))

def get_extension_from_headers(headers_str, fallback='.bin'):
    cd = re.search(r'filename[^;=\n]*=\s*["\']?([^"\';\n]+)', headers_str, re.I)
    if cd:
        ext = os.path.splitext(cd.group(1).strip())[1].lower()
        if ext: return ext
    ct = re.search(r'content-type:\s*([^\s;]+)', headers_str, re.I)
    CT_MAP = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'application/zip': '.zip', 'text/plain': '.txt', 'text/html': '.html',
        'image/png': '.png', 'image/jpeg': '.jpg', 'image/gif': '.gif', 'image/webp': '.webp',
    }
    if ct: return CT_MAP.get(ct.group(1).lower().strip(), fallback)
    return fallback

def download_image(img_url):
    """Descarga imagen a downloads/images/, devuelve path relativo desde pages/."""
    fname_hash = hashlib.md5(img_url.encode()).hexdigest()[:12]
    ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1].lower() or '.jpg'
    local_name = f"{fname_hash}{ext}"
    local_path = os.path.join(IMAGES_DIR, local_name)
    if os.path.exists(local_path):
        return f"../images/{local_name}"
    try:
        r = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '10', '-b', COOKIES_PATH, '-o', local_path, img_url],
            capture_output=True, timeout=15
        )
        if r.returncode == 0 and os.path.exists(local_path) and os.path.getsize(local_path) > 100:
            return f"../images/{local_name}"
    except Exception:
        pass
    if os.path.exists(local_path):
        os.remove(local_path)
    return None

def html_to_markdown(html_bytes, page_url):
    """Limpia HTML, descarga imágenes relevantes y convierte a Markdown sin links.

    Los links se eliminan (se conserva el texto del anchor).
    Las imágenes relevantes se descargan y referencian localmente.
    Los links a adjuntos y páginas van en INDEX.md, no aquí.
    """
    # Decodificar bytes a str antes de pasar a BeautifulSoup para preservar
    # correctamente el encoding UTF-8 (evita que BS4 detecte mal el charset)
    if isinstance(html_bytes, bytes):
        html_bytes = html_bytes.decode('utf-8', errors='replace')
    soup = BeautifulSoup(html_bytes, 'html.parser')

    # 1. Eliminar ruido estructural
    for tag in soup.find_all(['script','style','link','meta','noscript','svg',
                               'canvas','video','audio','iframe','object','embed',
                               'picture','form','button','input','select','textarea']):
        tag.decompose()
    # Eliminar iconos Font Awesome (generan __ vacíos en html2text)
    for tag in soup.find_all('i', class_=re.compile(r'fa|icon|glyphicon', re.I)):
        tag.decompose()
    for tag in soup.find_all(class_=re.compile(r'icono|icon-', re.I)):
        tag.decompose()
    # Eliminar elementos de navegación/layout por rol semántico
    for role in ['navigation','banner','complementary','contentinfo','search']:
        for el in soup.find_all(attrs={'role': role}): el.decompose()
    # Eliminar elementos de navegación/layout por clase CSS (exacta, no parcial)
    # IMPORTANTE: usar ^cls$ para no borrar clases como "page-header"
    for cls in ['nav','navbar','breadcrumb','sidebar','footer','header','menu',
                'cookie','modal','toolbar','megamenu','offcanvas','pagination']:
        for el in soup.find_all(class_=re.compile(r'^' + cls + r'$', re.I)):
            el.decompose()

    # 2. Área de contenido principal
    main = (soup.find('main') or soup.find('article') or
            soup.find(id=re.compile(r'content|main|article', re.I)) or soup.body or soup)

    # 3. Procesar imágenes — descargar las relevantes, eliminar decorativas
    for img in main.find_all('img'):
        if is_decorative_img(img):
            img.decompose()
            continue
        src = img.get('src', '')
        if not src: img.decompose(); continue
        abs_src = absolute_url(src, page_url)
        if not abs_src: img.decompose(); continue
        local_rel = download_image(abs_src)
        if local_rel:
            img['src'] = local_rel
            img.attrs = {k: v for k, v in img.attrs.items() if k in ('src','alt','width')}
        else:
            img['src'] = abs_src
            img.attrs = {k: v for k, v in img.attrs.items() if k in ('src','alt')}

    # 4. HTML → Markdown (sin links: ignore_links conserva el texto del anchor)
    h = html2text.HTML2Text()
    h.ignore_links     = True   # elimina href, conserva texto del anchor
    h.ignore_images    = False
    h.body_width       = 0
    h.unicode_snob     = True
    h.ignore_tables    = False
    h.bypass_tables    = False
    md = h.handle(str(main))
    md = re.sub(r'\n{3,}', '\n\n', md).strip()
    return md

# ── Playwright: descarga de páginas SPA ──────────────────────────────────────
def storybook_iframe_url(url):
    """Convierte URL de Storybook app shell a URL directa del iframe de docs.
    Ej: /?path=/docs/foundations-colors--docs → /iframe.html?viewMode=docs&id=foundations-colors
    Devuelve la URL original si no coincide el patrón."""
    import re as _re
    m = _re.search(r'/\?path=/docs/(.+?)(?:--docs)?$', url)
    if m:
        story_id = m.group(1)
        base = url.split('?')[0].rstrip('/')
        return f"{base}/iframe.html?viewMode=docs&id={story_id}"
    return url

def download_with_playwright(url, wait_selector, timeout_ms=10000):
    """Descarga HTML de una página SPA usando Chromium headless.
    Para Storybook: convierte automáticamente la URL al iframe directo de docs.
    Espera al selector CSS indicado antes de extraer el contenido."""
    # Storybook: navegar al iframe directamente (el contenido no está en la app shell)
    fetch_url = storybook_iframe_url(url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(fetch_url, wait_until='networkidle', timeout=30000)
        try:
            page.wait_for_selector(wait_selector, timeout=timeout_ms)
        except Exception:
            pass  # fallback: extraer lo que haya
        el = page.query_selector(wait_selector)
        html = el.inner_html() if el else page.content()
        browser.close()
        return html.encode('utf-8') if isinstance(html, str) else html


# ── Fase 1: Expansión — descubrir páginas enlazadas desde semillas ────────────
_expand = config.get('download', {}).get('expand', True)
html_cache   = {}                              # url → bytes (evita re-descarga)
expanded_map = {n['url']: n for n in pages_seed}  # url → node

if not _expand:
    print(f"\n  Fase 1: Expansión deshabilitada (expand=false) — solo páginas del filtro")
else:
    print(f"\n  Fase 1: Expansión desde {len(pages_seed)} páginas semilla...")
    for n in pages_seed:
        if n.get('spa'):
            continue  # SPA: se descargan con Playwright en Fase 3; no analizar sus links
        sys.stdout.write(f"\r  Analizando: {n.get('title', n['id'])[:55]:<55}")
        sys.stdout.flush()
        try:
            r = subprocess.run(
                ['curl', '-s', '-L', '--max-time', '15', '-b', COOKIES_PATH, n['url']],
                capture_output=True, timeout=20
            )
            if r.returncode != 0 or not r.stdout:
                continue
            html_cache[n['url']] = r.stdout
            soup = BeautifulSoup(r.stdout, 'html.parser')
            for a in soup.find_all('a', href=True):
                abs_href = absolute_url(a['href'], n['url'])
                if (abs_href
                        and abs_href not in expanded_map
                        and abs_href in url_to_node
                        and matches_keywords(url_to_node[abs_href])):
                    linked = url_to_node[abs_href]
                    expanded_map[abs_href] = linked
                    print(f"\n    + Enlazada: {linked.get('title', abs_href)}")
        except Exception as e:
            print(f"\n  [WARN] expansión {n['id']}: {e}")

seed_urls   = {n['url'] for n in pages_seed}
pages_extra = [n for n in expanded_map.values() if n['url'] not in seed_urls]
pages_all   = pages_seed + pages_extra
print(f"\n  Total páginas a descargar: {len(pages_all)}"
      f"  ({len(pages_seed)} semilla + {len(pages_extra)} enlazadas)\n")

# ── Construir page_filename_map (para nombrar archivos .md) ──────────────────
page_fname_map = {}  # url → nombre de fichero .md
for n in pages_all:
    title = n.get('title', n['id'])
    fname = f"{n['id']}-{slugify(title)}.md"
    page_fname_map[n['url']] = fname

# ── Fase 2: Descargar ficheros adjuntos ──────────────────────────────────────
print(f"  Fase 2: Descargando {len(files)} ficheros adjuntos...")
files_ok    = 0
ext_map     = {}
file_url_map = {n['url']: None for n in files}

for i, n in enumerate(files, 1):
    title     = n.get('title', n['id'])
    base_name = f"{n['id']}-{slugify(title)}"
    url       = n['url']
    sys.stdout.write(f"\r  [{i}/{len(files)}] {base_name[:55]:<55}")
    sys.stdout.flush()
    try:
        r_head = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '15', '-b', COOKIES_PATH,
             '-D', '-', '-o', '/dev/null', url],
            capture_output=True, text=True, timeout=20
        )
        ext        = get_extension_from_headers(r_head.stdout)
        final_name = f"{base_name}{ext}"
        out_path   = os.path.join(FILES_DIR, final_name)
        r = subprocess.run(
            ['curl', '-s', '-L', '--max-time', '30', '-b', COOKIES_PATH, '-o', out_path, url],
            capture_output=True, timeout=35
        )
        if r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            ext_map[f"{base_name}.bin"] = final_name
            file_url_map[url] = final_name
            files_ok += 1
        else:
            if os.path.exists(out_path): os.remove(out_path)
    except Exception as e:
        print(f"\n  [WARN] {n['id']}: {e}")

print(f"\n  Ficheros descargados: {files_ok}/{len(files)}")

# ── Fase 3: Descargar páginas y convertir a Markdown ─────────────────────────
print(f"\n  Fase 3: Descargando y convirtiendo {len(pages_all)} páginas a Markdown...")
pages_ok = 0

for i, n in enumerate(pages_all, 1):
    title    = n.get('title', n['id'])
    fname    = page_fname_map[n['url']]
    out_path = os.path.join(PAGES_DIR, fname)
    sys.stdout.write(f"\r  [{i}/{len(pages_all)}] {fname[:55]:<55}")
    sys.stdout.flush()
    try:
        if n.get('spa'):
            # Nodo SPA: usar Playwright en lugar de curl
            if not PLAYWRIGHT_AVAILABLE:
                print(f"\n  [WARN] Nodo SPA {n['id']} omitido: playwright no instalado")
                print(f"         Instalar con: pip install playwright && playwright install chromium")
                continue
            sys.stdout.write(f"\r  [{i}/{len(pages_all)}] [PW] {fname[:50]:<50}")
            sys.stdout.flush()
            html_bytes = download_with_playwright(n['url'], SPA_WAIT_SELECTOR, SPA_TIMEOUT_MS)
            if not html_bytes:
                print(f"\n  [WARN] Playwright no obtuvo contenido para {n['id']}")
                continue
        elif n['url'] in html_cache:
            # Usar caché si disponible (semillas ya descargadas en Fase 1)
            html_bytes = html_cache[n['url']]
        else:
            r = subprocess.run(
                ['curl', '-s', '-L', '--max-time', '15', '-b', COOKIES_PATH, n['url']],
                capture_output=True, timeout=20
            )
            if r.returncode != 0 or not r.stdout:
                continue
            html_bytes = r.stdout
        md = html_to_markdown(html_bytes, n['url'])

        # Adjuntos del nodo
        adj_lines = []
        seen_att = set()
        for att in n.get('attachments', []):
            url_att  = att.get('url', '') if isinstance(att, dict) else str(att)
            name_att = att.get('name', '') if isinstance(att, dict) else ''
            if not url_att or url_att in seen_att: continue
            seen_att.add(url_att)
            local = file_url_map.get(url_att)
            if local:
                ext  = os.path.splitext(local)[1]
                label = name_att if name_att.lower().endswith(ext.lower()) else (name_att or local) + ext
                adj_lines.append(f"- [{label}](../files/{local})")
            elif name_att:
                adj_lines.append(f"- {name_att} _(no descargado)_")

        if adj_lines:
            # Convertir "- [label](path)" → "<li><a href='path'>label</a></li>"
            def md_link_to_html(line):
                m = re.match(r"- \[([^\]]+)\]\(([^\)]+)\)", line)
                return f"<li><a href='{m.group(2)}'>{m.group(1)}</a></li>" if m else f"<li>{line[2:]}</li>"
            adj_cell = "<ul>" + "".join(md_link_to_html(l) for l in adj_lines) + "</ul>"
        else:
            adj_cell = "—"

        header = (
            f"# {title}\n\n"
            f"[← Volver al INDEX](../../INDEX.md)\n\n"
            f"| Aspecto | Valor |\n"
            f"|---------|-------|\n"
            f"| Fuente | [{n['url']}]({n['url']}) |\n"
            f"| Adjuntos | {adj_cell} |\n"
            f"\n---\n\n"
        )
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(header + md)
        pages_ok += 1
    except Exception as e:
        print(f"\n  [WARN] {n['id']}: {e}")

print(f"\n  Páginas convertidas: {pages_ok}/{len(pages_all)}")

# ── Fase 4: Guardar file-url-map.json (para COMMAND-5-GENERATE) ──────────────
FILE_URL_MAP_PATH = f"{_data_dir}/file-url-map.json"
with open(FILE_URL_MAP_PATH, 'w', encoding='utf-8') as f:
    json.dump({k: v for k, v in file_url_map.items() if v}, f, ensure_ascii=False, indent=2)
print(f"\n  file-url-map.json guardado ✓  ({files_ok} entradas)")
print(f"  Ejecutar COMMAND-5-GENERATE para generar INDEX.md")

# ── Fase 5: Actualizar config ─────────────────────────────────────────────────
now_ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
config.setdefault('session', {})['download_status']    = 'ok'
config.setdefault('session', {})['download_timestamp'] = now_ts
config.setdefault('metrics', {})['pages_downloaded']   = pages_ok
config.setdefault('metrics', {})['files_downloaded']   = files_ok
images_count = len(os.listdir(IMAGES_DIR))
config['metrics']['images_downloaded'] = images_count
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# ── Fase 6: Eliminar credenciales (CRÍTICO) ───────────────────────────────────
if os.path.exists(SESSION_TMP):
    os.remove(SESSION_TMP)
    creds_status = "eliminado ✓"
else:
    creds_status = "no existía"
print(f"  scrapper-session.tmp {creds_status}")

# ── Resumen ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"  DESCARGA COMPLETADA")
print(f"{'═'*60}")
print(f"  Páginas (Markdown):    {pages_ok}  → downloads/pages/")
print(f"  Ficheros adjuntos:     {files_ok}  → downloads/files/")
print(f"  Imágenes:              {images_count}  → downloads/images/")
print(f"  Credenciales:          {creds_status}")
print(f"{'═'*60}\n")
