#!/usr/bin/env python3
# ---
# version: 1.8
# description: Script de crawling para doc-scrapper - COMMAND-3.1-CRAWL
# agent: doc-scrapper
# author: rmompo@gmail.com
# created: 2026-02-24T00:00:00
# updated: 2026-03-06T00:00:00
# ---
# Novedades v1.8:
#   - CONFIG_PATH desde sys.argv[1] (con fallback al path mova3)
#   - Paths derivados de config["output"]["folder"] en lugar de hardcodeados
#   - Detección automática de SPA (detect_spa, try_inventory, build_nodes_from_inventory)
#   - Si SPA detectada + inventario disponible: genera nodos sin BFS (run_spa_inventory)
#   - Nodos SPA marcados con "spa": true para uso de COMMAND-DOWNLOAD

import json, os, re, time, hashlib, subprocess, sys
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup

# ── Configuración ────────────────────────────────────────────────────────────
CONFIG_PATH = sys.argv[1] if len(sys.argv) > 1 else "generated/scrapp/mova3/data/scrapper-config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

_data_dir          = config["output"]["folder"] + "/data"
COOKIES_PATH       = f"{_data_dir}/scrapper-cookies.txt"
SESSION_PATH       = f"{_data_dir}/scrapper-session.tmp"
WEBMAP_META_PATH   = f"{_data_dir}/web-map-meta.json"
WEBMAP_NODES_PATH  = f"{_data_dir}/web-map-nodes.jsonl"
EXCLUDED_PATH      = f"{_data_dir}/web-map-excluded.jsonl"

START_URL   = config["crawl"]["start_url"]
BASE_DOMAIN = config["crawl"]["base_domain"]
MAX_DEPTH   = config["crawl"]["max_depth"]
PAUSE_MS    = config["crawl"].get("pause_ms", 300)

# ── Constantes desde config ───────────────────────────────────────────────────
_crawl = config.get("crawl", {})
_html  = config.get("html", {})

STATIC_EXTENSIONS      = set(_crawl.get("static_extensions", [
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp',
    '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.map',
    '.mp4', '.mp3', '.avi', '.mov', '.webm', '.ogg',
]))
FILE_EXTENSIONS        = set(_crawl.get("file_extensions", [
    '.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.txt',
]))
FILE_PATTERNS          = _crawl.get("file_patterns", ['/download/', '/send/', '/component/jdownloads/'])
URL_IGNORE_PATTERNS    = _crawl.get("url_ignore_patterns", [
    'tmpl=component', 'print=1', 'format=pdf', 'format=feed',
    'format=atom', 'format=raw', 'limitstart=', 'task=',
    'option=com_search', 'option=com_users', 'option=com_contact',
    'option=com_login', '/administrator/', '/logout', '/login',
    'javascript:', 'mailto:', 'tel:',
])
TAGS_TO_REMOVE         = _html.get("tags_to_remove", [
    'script', 'style', 'link', 'meta', 'noscript',
    'svg', 'canvas', 'video', 'audio', 'iframe', 'object', 'embed', 'picture',
])
ROLES_TO_REMOVE        = _html.get("roles_to_remove", [
    'navigation', 'banner', 'complementary', 'contentinfo', 'search',
])
CLASSES_TO_REMOVE      = _html.get("classes_to_remove", [
    'nav', 'navbar', 'breadcrumb', 'pagination', 'sidebar',
    'footer', 'header', 'menu', 'cookie-banner', 'cookie-notice',
    'modal', 'social-share', 'ads', 'advertisement', 'toolbar',
    'topbar', 'megamenu', 'offcanvas',
])
DECORATIVE_IMG_CLASSES = set(_html.get("decorative_img_classes", [
    'icon', 'logo', 'avatar', 'emoji', 'bullet', 'badge', 'spinner',
]))
SELECTORS              = _crawl.get("selectors", [])
SAVE_INTERVAL          = _crawl.get("save_interval", 20)

# ── SPA: configuración ───────────────────────────────────────────────────────
_parsed_start     = urlparse(START_URL)
BASE_URL          = f"{_parsed_start.scheme}://{_parsed_start.netloc}{_parsed_start.path}"
if not BASE_URL.endswith('/'):
    BASE_URL = BASE_URL.rsplit('/', 1)[0] + '/'

_spa_cfg          = config.get('spa', {})
SPA_MODE          = _spa_cfg.get('mode', 'static')
SPA_WAIT_SELECTOR = _spa_cfg.get('wait_selector', '.sbdocs-wrapper')
SPA_TIMEOUT_MS    = _spa_cfg.get('wait_timeout_ms', 10000)
SPA_DOCS_TAG      = _spa_cfg.get('docs_filter_tag', 'docs')
SPA_INVENTORY_URL = _spa_cfg.get('inventory_url', None)

# ── Estado global ────────────────────────────────────────────────────────────
visited_urls     = set()   # URLs ya procesadas o excluidas (dedup de procesamiento)
queued_urls      = set()   # URLs ya encoladas (dedup de cola)
content_hashes   = set()
web_map_nodes    = {}      # {id → nodo} en memoria
url_index        = {}      # {url → id} construido incrementalmente
nodes_count      = 0       # contador para SAVE_INTERVAL
node_flush_ptr   = 0       # índice del próximo nodo a escribir en JSONL
excluded         = []
excl_flush_ptr   = 0       # índice de la próxima exclusión a escribir en JSONL
node_counter     = 0
http_requests    = 0

# ── Carga de estado previo (resume) ──────────────────────────────────────────
if os.path.exists(WEBMAP_META_PATH):
    try:
        with open(WEBMAP_META_PATH, encoding='utf-8') as _f:
            _meta = json.load(_f)
        url_index     = _meta.get('url_index', {})
        node_counter  = _meta.get('node_counter', 0)
        http_requests = _meta.get('http_requests', 0)
        print(f"  [RESUME] meta cargada — {node_counter} nodos previos")
    except Exception as _e:
        print(f"  [RESUME] No se pudo cargar meta: {_e}")

if os.path.exists(WEBMAP_NODES_PATH):
    try:
        with open(WEBMAP_NODES_PATH, encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line:
                    continue
                _n = json.loads(_line)
                web_map_nodes[_n['id']] = _n
                visited_urls.add(_n['url'])
                if _n.get('content_hash'):
                    content_hashes.add(_n['content_hash'])
        nodes_count    = len(web_map_nodes)
        node_flush_ptr = nodes_count
        print(f"  [RESUME] {nodes_count} nodos cargados de {WEBMAP_NODES_PATH}")
    except Exception as _e:
        print(f"  [RESUME] Error cargando nodos: {_e}")

if os.path.exists(EXCLUDED_PATH):
    try:
        with open(EXCLUDED_PATH, encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if not _line:
                    continue
                _e = json.loads(_line)
                excluded.append(_e)
                visited_urls.add(_e['url'])
        excl_flush_ptr = len(excluded)
        print(f"  [RESUME] {len(excluded)} exclusiones cargadas de {EXCLUDED_PATH}")
    except Exception:
        pass

# queued_urls arranca con todo lo ya procesado/excluido para no re-encolar en resume
queued_urls.update(visited_urls)

def next_id():
    global node_counter
    node_counter += 1
    return f"n{node_counter:03d}"

# ── Guardado progresivo ──────────────────────────────────────────────────────
def save_progress(final=False):
    """Guardado optimizado con ficheros separados:
      - web-map-nodes.jsonl   : APPEND-ONLY durante crawl; rewrite completo solo en final
      - web-map-excluded.jsonl: APPEND-ONLY siempre
      - web-map-meta.json     : reescritura del fichero pequeño (meta + url_index)
    Con final=True resuelve _raw_links → IDs y reescribe el JSONL de nodos."""
    global node_flush_ptr, excl_flush_ptr
    import datetime as _dt

    if final:
        # Resolver enlaces usando url_index (O(1) por enlace)
        for node in web_map_nodes.values():
            raw = node.pop('_raw_links', [])
            node['links'] = [url_index[u] for u in raw if u in url_index]
        # Reescritura completa del JSONL con links resueltos (única vez)
        with open(WEBMAP_NODES_PATH, 'w', encoding='utf-8') as f:
            for node in web_map_nodes.values():
                f.write(json.dumps(node, ensure_ascii=False) + '\n')
        node_flush_ptr = len(web_map_nodes)
    else:
        # Append solo los nodos nuevos desde el último flush
        new_ids = list(web_map_nodes.keys())[node_flush_ptr:]
        if new_ids:
            with open(WEBMAP_NODES_PATH, 'a', encoding='utf-8') as f:
                for nid in new_ids:
                    node = web_map_nodes[nid]
                    record = {k: v for k, v in node.items() if k != '_raw_links'}
                    record['links'] = []  # sin resolver hasta el save final
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            node_flush_ptr += len(new_ids)

    # Append nuevas exclusiones
    new_excl = excluded[excl_flush_ptr:]
    if new_excl:
        with open(EXCLUDED_PATH, 'a', encoding='utf-8') as f:
            for e in new_excl:
                f.write(json.dumps(e, ensure_ascii=False) + '\n')
        excl_flush_ptr += len(new_excl)

    # Reescribir meta.json (pequeño — siempre)
    pages = sum(1 for n in web_map_nodes.values() if n.get('type') == 'page')
    files = sum(1 for n in web_map_nodes.values() if n.get('type') == 'file')
    meta = {
        "format_version": "2.0",
        "updated": _dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "crawl_status": "done" if final else "in_progress",
        "node_counter": node_counter,
        "http_requests": http_requests,
        "stats": {"pages": pages, "files": files, "excluded": excl_flush_ptr},
        "url_index": url_index
    }
    with open(WEBMAP_META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.flush()

# ── 2.1 Pre-filtro de URL ────────────────────────────────────────────────────
def should_skip_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in STATIC_EXTENSIONS):
        return True, 'static_resource'
    full = url.lower()
    if any(pat in full for pat in URL_IGNORE_PATTERNS):
        return True, 'ignored_pattern'
    return False, None

def normalize_url(url):
    p = urlparse(url)
    # quitar fragmento, normalizar scheme a https
    return urlunparse((p.scheme, p.netloc, p.path.rstrip('/') or '/', p.params, p.query, ''))

def is_file_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in FILE_EXTENSIONS):
        return True
    if any(pat in url for pat in FILE_PATTERNS):
        return True
    return False

# ── 2.2 HEAD check ──────────────────────────────────────────────────────────
def head_check(url):
    global http_requests
    http_requests += 1
    try:
        result = subprocess.run(
            ['curl', '-s', '-I', '--max-redirs', '5', '-b', COOKIES_PATH,
             '-w', '\n%{http_code}', '--connect-timeout', '10', url],
            capture_output=True, text=True, timeout=15
        )
        headers = result.stdout.lower()
        content_type = ''
        for line in headers.splitlines():
            if line.startswith('content-type:'):
                content_type = line.split(':', 1)[1].strip()
                break
        return content_type
    except Exception:
        return ''

# ── GET ──────────────────────────────────────────────────────────────────────
def get_page(url):
    """Devuelve (html, final_url). final_url permite detectar redirección al login."""
    global http_requests
    http_requests += 1
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-redirs', '5', '-b', COOKIES_PATH,
             '--connect-timeout', '10', '-L',
             '-w', '\n__FINAL_URL__%{url_effective}',
             url],
            capture_output=True, text=True, timeout=30
        )
        out = result.stdout
        if '\n__FINAL_URL__' in out:
            parts = out.rsplit('\n__FINAL_URL__', 1)
            return parts[0], parts[1].strip()
        return out, url
    except Exception:
        return '', url

# ── 2.3 Canonical ───────────────────────────────────────────────────────────
def get_canonical(soup, current_url):
    tag = soup.find('link', rel='canonical')
    if tag and tag.get('href'):
        return normalize_url(urljoin(current_url, tag['href'].strip()))
    return None

# ── 2.4 Limpieza HTML ───────────────────────────────────────────────────────
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup.find_all(TAGS_TO_REMOVE):
        tag.decompose()
    for role in ROLES_TO_REMOVE:
        for el in soup.find_all(attrs={'role': role}):
            el.decompose()
    for cls in CLASSES_TO_REMOVE:
        for el in soup.find_all(class_=lambda c: c and cls in ' '.join(c).lower()):
            el.decompose()
    return soup

# ── 2.4b Imágenes de contenido ──────────────────────────────────────────────
def process_content_images(content_area):
    image_refs = []
    for img in content_area.find_all('img'):
        src = img.get('src', '').strip()
        alt = img.get('alt', '').strip()
        classes = ' '.join(img.get('class', [])).lower()
        try:
            w = int(img.get('width', 999))
            h = int(img.get('height', 999))
        except (ValueError, TypeError):
            w, h = 999, 999

        is_decorative = (
            any(c in classes for c in DECORATIVE_IMG_CLASSES)
            or w < 50 or h < 50
            or not src
        )
        if is_decorative:
            img.decompose()
        else:
            label = alt if len(alt) > 10 else src.split('/')[-1].split('?')[0]
            img.replace_with(f'\n[Imagen: {label}]\n')
            image_refs.append({'src': src, 'alt': alt})

    for figure in content_area.find_all('figure'):
        figcaption = figure.find('figcaption')
        caption = figcaption.get_text(strip=True) if figcaption else ''
        if caption:
            figure.replace_with(f'\n[Figura: {caption}]\n')
        else:
            figure.decompose()

    return image_refs

# ── 2.5 Extracción de texto ──────────────────────────────────────────────────
def find_selector_target(soup, current_url):
    """Devuelve el elemento indicado por selector de config si la URL coincide.
    Devuelve None si no hay regla aplicable o el selector no encuentra nada (fallback)."""
    for rule in SELECTORS:
        if rule.get("url_pattern", "") in current_url:
            sel   = rule.get("selector", "")
            stype = rule.get("selector_type", "css")
            try:
                if stype == "xpath":
                    from lxml import etree
                    import lxml.etree as ET
                    tree = etree.fromstring(str(soup), etree.HTMLParser())
                    nodes = tree.xpath(sel)
                    if nodes:
                        return BeautifulSoup(ET.tostring(nodes[0], encoding='unicode'), 'html.parser')
                else:  # css (por defecto)
                    result = soup.select_one(sel)
                    if result:
                        return result
            except Exception:
                pass  # fallback a detección automática
    return None

def extract_content(soup, current_url=""):
    target = find_selector_target(soup, current_url)
    if target is None:
        main = (
            soup.find('main') or
            soup.find(attrs={'role': 'main'}) or
            soup.find('article') or
            soup.find(id=lambda i: i and 'content' in i.lower()) or
            soup.find(class_=lambda c: c and 'content' in ' '.join(c).lower())
        )
        target = main if main else (soup.find('body') or soup)
    image_refs = process_content_images(target)
    text = target.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()
    return text, image_refs

def extract_title(soup):
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    title = soup.find('title')
    if title:
        t = title.get_text(strip=True)
        return t.split('|')[0].split('-')[0].strip()
    return ''

def extract_description(text):
    for sentence in text.split('.'):
        s = sentence.strip()
        if len(s) > 50:
            return s[:300]
    return text[:300]

# ── 2.6 Hash dedup ──────────────────────────────────────────────────────────
def content_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# ── 2.7 Extracción de enlaces ───────────────────────────────────────────────
def extract_links_and_files(soup, current_url):
    pages, files = [], []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('#'):
            continue
        full_url = urljoin(current_url, href)
        parsed = urlparse(full_url)
        if BASE_DOMAIN not in parsed.netloc:
            continue
        path = parsed.path.lower()
        if any(path.endswith(ext) for ext in STATIC_EXTENSIONS):
            continue
        if is_file_url(full_url):
            files.append({
                'url': full_url,
                'name': path.split('/')[-1],
                'type': path.rsplit('.', 1)[-1] if '.' in path else 'unknown'
            })
        else:
            pages.append(normalize_url(full_url))
    return pages, files

# ── Pipeline principal ───────────────────────────────────────────────────────
def process_url(url, depth, discovered_from_id):
    global visited_urls, nodes_count

    url = normalize_url(url)
    if url in visited_urls:
        return []
    visited_urls.add(url)

    # 2.1 Pre-filtro
    skip, reason = should_skip_url(url)
    if skip:
        excluded.append({'url': url, 'depth': depth, 'excluded_reason': reason})
        return []

    # Detectar si es fichero antes del HEAD (por URL)
    if is_file_url(url):
        node_id = next_id()
        fname = urlparse(url).path.split('/')[-1]
        node = {
            'id': node_id, 'url': url, 'type': 'file',
            'title': fname, 'description': f'Fichero adjunto: {fname}',
            'links': [], 'depth': depth, 'discovered_from': discovered_from_id,
            'created_date': None, 'content_hash': None, 'images': [],
            'attachments': [{'url': url, 'name': fname,
                             'type': fname.rsplit('.', 1)[-1] if '.' in fname else 'unknown'}],
            'processed': True,
        }
        web_map_nodes[node_id] = node
        url_index[url] = node_id
        nodes_count += 1
        if nodes_count % SAVE_INTERVAL == 0:
            save_progress()
        print(f"  [FILE] {fname}")
        return []

    # 2.2 HEAD check
    content_type = head_check(url)
    if content_type:
        if any(t in content_type for t in ['text/css', 'application/javascript', 'image/']):
            excluded.append({'url': url, 'depth': depth, 'excluded_reason': 'non_html_content'})
            return []
        # Si es PDF/ZIP por content-type, registrar como file
        if any(t in content_type for t in ['application/pdf', 'application/zip',
                                             'application/msword', 'application/vnd']):
            node_id = next_id()
            fname = urlparse(url).path.split('/')[-1]
            ext = content_type.split('/')[-1].split(';')[0].strip()
            node = {
                'id': node_id, 'url': url, 'type': 'file',
                'title': fname, 'description': f'Fichero adjunto: {fname}',
                'links': [], 'depth': depth, 'discovered_from': discovered_from_id,
                'created_date': None, 'content_hash': None, 'images': [],
                'attachments': [{'url': url, 'name': fname, 'type': ext}],
                'processed': True,
            }
            web_map_nodes[node_id] = node
            url_index[url] = node_id
            nodes_count += 1
            if nodes_count % SAVE_INTERVAL == 0:
                save_progress()
            print(f"  [FILE via HEAD] {fname}")
            return []

    # GET completo
    raw_html, final_url = get_page(url)
    if not raw_html:
        excluded.append({'url': url, 'depth': depth, 'excluded_reason': 'fetch_error'})
        return []

    # Detección de redirección al login (sesión expirada)
    login_url = config['auth'].get('login_url') or ''
    if final_url and login_url and (login_url in final_url or
                      ('option=com_users' in final_url and 'task=user.login' in final_url)):
        print(f"\n  ⚠ Sesión expirada detectada al procesar: {url}")
        print("  Guardando progreso antes de salir...")
        save_progress()
        print("  → Ejecutar COMMAND-2-LOGIN para renovar la sesión y relanzar el crawl.")
        print("    El crawl reanudará automáticamente desde el último nodo guardado.")
        sys.exit(42)  # señal al modelo: re-login necesario

    soup_raw = BeautifulSoup(raw_html, 'html.parser')

    # 2.3 Canonical
    canonical = get_canonical(soup_raw, url)
    if canonical and canonical != url:
        if canonical in visited_urls:
            excluded.append({'url': url, 'depth': depth, 'excluded_reason': 'canonical_redirect'})
            return []
        else:
            visited_urls.add(url)  # marcar original como visitado
            # encolar el canonical en su lugar
            return [{'url': canonical, 'depth': depth, 'from': discovered_from_id}]

    # 2.4 Limpieza
    soup = clean_html(raw_html)

    # Extracción de título (del soup limpio)
    title = extract_title(soup)

    # 2.7 Extracción de enlaces — sobre soup limpio (sin nav/footer/sidebar)
    links_pages, links_files = extract_links_and_files(soup, url)

    def build_next_queue(from_id):
        """Encola los enlaces descubiertos aunque la página se excluya.
        Usa queued_urls para que cada URL se encole una sola vez,
        evitando GETs duplicados sin impedir el procesamiento posterior."""
        q = []
        if depth < MAX_DEPTH:
            for link_url in links_pages:
                if link_url not in queued_urls:
                    queued_urls.add(link_url)
                    q.append({'url': link_url, 'depth': depth + 1, 'from': from_id})
        return q

    # 2.5 Extracción de texto + imágenes
    text, image_refs = extract_content(soup, url)

    word_count = len(text.split())

    # 2.6 Hash dedup — excluir página pero seguir sus enlaces
    h = content_hash(text)
    if h in content_hashes:
        excluded.append({'url': url, 'depth': depth, 'excluded_reason': 'duplicate_content'})
        print(f"  [SKIP dup] {url[:80]} | siguiendo {len(links_pages)} enlaces")
        return build_next_queue(discovered_from_id)
    content_hashes.add(h)

    description = extract_description(text)

    # Construir nodo
    node_id = next_id()
    node = {
        'id': node_id,
        'url': url,
        'type': 'page',
        'title': title or url.split('/')[-1],
        'description': description,
        'links': [],  # se rellenará con IDs en post-proceso
        'depth': depth,
        'discovered_from': discovered_from_id,
        'created_date': None,
        'content_hash': h,
        'images': image_refs,
        'attachments': links_files,
        '_raw_links': links_pages,  # temporal, se elimina al final
        'processed': True,
    }
    web_map_nodes[node_id] = node
    url_index[url] = node_id
    nodes_count += 1
    if nodes_count % SAVE_INTERVAL == 0:
        save_progress()
    print(f"  [PAGE] (d{depth}) {title or url[:80]}"
          f" | {word_count}w | {len(image_refs)} imgs | {len(links_files)} files")

    # Encolar páginas descubiertas
    next_queue = build_next_queue(node_id)
    if depth < MAX_DEPTH:
        # Registrar ficheros adjuntos como nodos file
        for finfo in links_files:
            furl = normalize_url(finfo['url'])
            if furl not in visited_urls:
                visited_urls.add(furl)
                fnode_id = next_id()
                fnode = {
                    'id': fnode_id, 'url': furl, 'type': 'file',
                    'title': finfo['name'],
                    'description': f"Fichero adjunto: {finfo['name']}",
                    'links': [], 'depth': depth + 1, 'discovered_from': node_id,
                    'created_date': None, 'content_hash': None, 'images': [],
                    'attachments': [finfo],
                    '_raw_links': [],
                    'processed': True,
                }
                web_map_nodes[fnode_id] = fnode
                url_index[furl] = fnode_id
                nodes_count += 1

    return next_queue

# ── SPA: detección e inventario ───────────────────────────────────────────────
def _curl_get_simple(url):
    """GET sin cookies ni auth (para detección SPA e inventario)."""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-redirs', '3', '--connect-timeout', '10', '-L', url],
            capture_output=True, text=True, timeout=20
        )
        return result.stdout
    except Exception:
        return ''


def detect_spa(url):
    """Devuelve True si la URL parece SPA: pocas palabras + div raíz SPA conocido."""
    html = _curl_get_simple(url)
    if not html:
        return False
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    word_count = len(text.split())
    has_spa_root = bool(
        soup.find('div', id=lambda i: i and i in ('root', 'app', 'storybook-root'))
        or soup.find('app-root')
        or soup.find(id='storybook-root')
    )
    result = word_count < 50 and has_spa_root
    print(f"  [SPA] detect_spa: {word_count} palabras, raíz SPA={has_spa_root} → {result}")
    return result


def try_inventory(base_url):
    """Intenta obtener el inventario Storybook desde index.json (v5/v6/v7) o stories.json (v3).
    Retorna lista de {id, title} o None si no está disponible."""
    urls_to_try = [SPA_INVENTORY_URL] if SPA_INVENTORY_URL else [
        base_url + 'index.json',
        base_url + 'stories.json',
    ]
    for url in urls_to_try:
        if not url:
            continue
        print(f"  [SPA] Intentando inventario: {url}")
        raw = _curl_get_simple(url)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        # Storybook v5/v6/v7: {"entries": {id: {type, title, ...}}}
        if 'entries' in data:
            entries = [
                {'id': k, 'title': v.get('title', k)}
                for k, v in data['entries'].items()
                if v.get('type', '') == SPA_DOCS_TAG
            ]
            print(f"  [SPA] inventario v5/v6/v7 desde {url}: {len(entries)} docs")
            return entries
        # Storybook v3: {"stories": {id: {tags, name, ...}}}
        if 'stories' in data:
            entries = [
                {'id': k, 'title': v.get('name', k)}
                for k, v in data['stories'].items()
                if SPA_DOCS_TAG in v.get('tags', [])
            ]
            print(f"  [SPA] inventario v3 desde {url}: {len(entries)} docs")
            return entries
    return None


def build_nodes_from_inventory(entries, base_url):
    """Construye nodos web-map desde el inventario Storybook. Marca cada nodo con spa=True."""
    nodes = []
    for entry in entries:
        entry_id = entry['id']
        title    = entry['title']
        url      = f"{base_url}?path=/docs/{entry_id}"
        nid      = next_id()
        node = {
            'id': nid,
            'url': url,
            'type': 'page',
            'title': title,
            'description': title,
            'links': [],
            'depth': 0,
            'discovered_from': 'inventory',
            'created_date': None,
            'content_hash': None,
            'images': [],
            'attachments': [],
            'spa': True,
            'processed': True,
        }
        web_map_nodes[nid] = node
        url_index[url] = nid
        nodes.append(node)
    return nodes


def run_spa_inventory():
    """Pipeline SPA: detecta SPA, obtiene inventario, genera nodos y guarda.
    Retorna True si se ejecutó el pipeline SPA (saltarse el BFS), False si no."""
    import datetime
    import time as t_module
    start_time = t_module.time()

    print(f"\n{'═'*55}")
    print(f"  FASE 0b — Detección SPA e inventario")
    print(f"  Start URL : {START_URL}")
    print(f"  Base URL  : {BASE_URL}")
    print(f"  SPA mode  : {SPA_MODE}")
    print(f"{'═'*55}\n")

    spa_detected = (SPA_MODE == 'playwright') or detect_spa(START_URL)
    if not spa_detected:
        print("  [SPA] No detectada — continuando con BFS estándar\n")
        return False

    print(f"  [SPA] Detectada → buscando inventario...")
    entries = try_inventory(BASE_URL)
    if not entries:
        print("  [SPA] Sin inventario disponible — continuando con BFS estándar\n")
        return False

    print(f"  [SPA] Construyendo {len(entries)} nodos desde inventario...")
    build_nodes_from_inventory(entries, BASE_URL)

    # Crear directorio de salida si no existe
    os.makedirs(_data_dir, exist_ok=True)

    # Guardar nodos (save_progress(final=True) resuelve _raw_links, aquí no hay)
    save_progress(final=True)

    # Actualizar config
    elapsed = t_module.time() - start_time
    config['session']['crawl_status']    = 'ok'
    config['session']['crawl_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    config['metrics']['pages_total']     = len(web_map_nodes)
    config['metrics']['pages_included']  = len(web_map_nodes)
    config['metrics']['pages_excluded']  = 0
    config['metrics']['files_found']     = 0
    config['metrics']['http_requests']   = 1  # solo GET a start_url para detección
    config['metrics']['crawl_duration_s'] = round(elapsed, 1)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n{'═'*55}")
    print(f"  RESUMEN SPA")
    print(f"{'═'*55}")
    print(f"  Nodos generados (spa=true): {len(web_map_nodes)}")
    print(f"  Duración:                   {round(elapsed, 1)}s")
    print(f"  web-map-nodes   → {WEBMAP_NODES_PATH}")
    print(f"  web-map-meta    → {WEBMAP_META_PATH}")
    print(f"{'═'*55}\n")
    return True


# ── BFS ──────────────────────────────────────────────────────────────────────
def run_crawl():
    import time as t_module
    start_time = t_module.time()

    print(f"\n{'═'*55}")
    print(f"  INICIANDO CRAWL")
    print(f"  Start URL : {START_URL}")
    print(f"  Dominio   : {BASE_DOMAIN}")
    print(f"  Max depth : {MAX_DEPTH}")
    print(f"{'═'*55}\n")

    queue = deque([{'url': START_URL, 'depth': 0, 'from': 'root'}])
    queued_urls.add(normalize_url(START_URL))

    while queue:
        item = queue.popleft()
        url, depth, from_id = item['url'], item['depth'], item['from']

        if depth > MAX_DEPTH:
            continue

        new_items = process_url(url, depth, from_id)
        for ni in new_items:
            queue.append(ni)

        time.sleep(PAUSE_MS / 1000)

    elapsed = t_module.time() - start_time

    # Guardado final: resuelve _raw_links a IDs y escribe versión definitiva
    save_progress(final=True)

    # Actualizar métricas en config
    pages = [n for n in web_map_nodes.values() if n['type'] == 'page']
    files = [n for n in web_map_nodes.values() if n['type'] == 'file']
    config['session']['crawl_status'] = 'ok'
    import datetime
    config['session']['crawl_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    config['metrics']['pages_total'] = nodes_count
    config['metrics']['pages_included'] = len(pages)
    config['metrics']['pages_excluded'] = len(excluded)
    config['metrics']['files_found'] = len(files)
    config['metrics']['http_requests'] = http_requests
    config['metrics']['crawl_duration_s'] = round(elapsed, 1)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # Resumen
    by_reason = {}
    for e in excluded:
        r = e.get('excluded_reason', 'unknown')
        by_reason[r] = by_reason.get(r, 0) + 1

    print(f"\n{'═'*55}")
    print(f"  RESUMEN DE EXPLORACIÓN")
    print(f"{'═'*55}")
    print(f"  Páginas incluidas:          {len(pages)}")
    print(f"  Ficheros adjuntos:          {len(files)}")
    print(f"  Imágenes de contenido:      {sum(len(n.get('images', [])) for n in pages)}")
    print(f"  URLs descartadas:           {len(excluded)}")
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"    · {reason:<30} {count}")
    print(f"  Peticiones HTTP:            {http_requests}")
    print(f"  Duración:                   {round(elapsed,1)}s")
    print(f"{'═'*55}\n")
    print(f"  web-map-meta    → {WEBMAP_META_PATH}")
    print(f"  web-map-nodes   → {WEBMAP_NODES_PATH}")
    print(f"  excluded        → {EXCLUDED_PATH}")
    print(f"{'═'*55}\n")

if __name__ == '__main__':
    if SPA_MODE != 'static':
        if run_spa_inventory():
            sys.exit(0)
    run_crawl()
