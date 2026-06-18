#!/usr/bin/env python3
# ---
# version: 1.1
# description: Filtrado del web-map por tópico y keywords — COMMAND-5-FILTER
# agent: doc-scrapper
# author: rmompo@gmail.com
# created: 2026-02-24T00:00:00
# updated: 2026-03-09T00:00:00
# ---

import json, datetime, subprocess, hashlib, re, sys, os

DEFAULT_CONFIG = "generated/scrapp/mova3/data/scrapper-config.json"
CONFIG_PATH    = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG

with open(CONFIG_PATH, encoding='utf-8') as f:
    _cfg_pre = json.load(f)

_folder           = _cfg_pre["output"]["folder"]
_data             = os.path.join(_folder, "data")
WEBMAP_META_PATH  = os.path.join(_data, "web-map-meta.json")
WEBMAP_NODES_PATH = os.path.join(_data, "web-map-nodes.jsonl")
EXCLUDED_PATH     = os.path.join(_data, "web-map-excluded.jsonl")
FILTERED_PATH     = os.path.join(_data, "web-map-filtered.jsonl")
COOKIES_PATH      = os.path.join(_data, "scrapper-cookies.txt")

print(f"\n{'═'*60}")
print(f"  COMMAND-4-FILTER — Filtrado del web-map")
print(f"{'═'*60}\n")

# ── 1. Leer configuración ─────────────────────────────────────────────────────
config = _cfg_pre

topic    = config['filter']['topic']
keywords = [kw.lower() for kw in config['filter']['keywords']]
enrich   = config['filter'].get('enrich', False)

print(f"  Tópico   : {topic[:80]}...")
print(f"  Keywords : {keywords}")
print(f"  Enrich   : {enrich}")

# ── 2. Cargar nodos ───────────────────────────────────────────────────────────
nodes      = {}   # {id → node}
node_order = []

with open(WEBMAP_NODES_PATH, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        node = json.loads(line)
        nodes[node['id']] = node
        node_order.append(node['id'])

print(f"\n  Nodos cargados: {len(node_order)}  (pages: {sum(1 for n in nodes.values() if n['type']=='page')}, files: {sum(1 for n in nodes.values() if n['type']=='file')})\n")

# ── 3. Función de matching ────────────────────────────────────────────────────
def matches_keywords(node, keywords):
    """Devuelve True si el nodo es relevante según keywords."""
    searchable = ' '.join([
        node.get('title', '') or '',
        node.get('description', '') or '',
        node.get('url', '') or '',
    ]).lower()
    return any(kw in searchable for kw in keywords)

# ── 4. Filtrar páginas ────────────────────────────────────────────────────────
included_page_ids = set()
included_file_ids = set()
excluded_new      = []

for nid in node_order:
    node = nodes[nid]
    if node['type'] == 'page':
        if matches_keywords(node, keywords):
            included_page_ids.add(nid)

print(f"  Páginas incluidas por keyword: {len(included_page_ids)}")

# ── 5. Filtrar ficheros ────────────────────────────────────────────────────────
# Incluir fichero si:
#   (a) Su título/URL contiene keyword, O
#   (b) Aparece en attachments de una página incluida
included_page_att_urls = set()
for nid in included_page_ids:
    for att in nodes[nid].get('attachments', []):
        if isinstance(att, dict):
            included_page_att_urls.add(att.get('url', ''))
        elif isinstance(att, str):
            included_page_att_urls.add(att)

for nid in node_order:
    node = nodes[nid]
    if node['type'] == 'file':
        if node['url'] in included_page_att_urls or matches_keywords(node, keywords):
            included_file_ids.add(nid)

print(f"  Ficheros incluidos:            {len(included_file_ids)}")

included_all = included_page_ids | included_file_ids
excluded_cnt = len(nodes) - len(included_all)
print(f"  Nodos excluidos (filtro):      {excluded_cnt}\n")

# ── 6. Enriquecimiento (si enrich=true y red disponible) ─────────────────────
network_ok = False
if enrich:
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '5',
             '-b', COOKIES_PATH, 'https://intranet.comunidad.madrid/arquitecturasw/index.php'],
            capture_output=True, text=True, timeout=10
        )
        network_ok = result.stdout.strip() in ('200', '301', '302')
    except Exception:
        network_ok = False

    if network_ok:
        print(f"  Enriquecimiento: sesión activa — iniciando...")
    else:
        print(f"  Enriquecimiento: sin acceso a la intranet — omitido (datos de crawl conservados)")
        enrich = False

if enrich and network_ok:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [WARN] BeautifulSoup no disponible — enriquecimiento omitido")
        enrich = False

if enrich and network_ok:
    enriched = 0
    total_pages = len(included_page_ids)
    for i, nid in enumerate(included_page_ids, 1):
        node = nodes[nid]
        sys.stdout.write(f"\r  Enriqueciendo {i}/{total_pages}...")
        sys.stdout.flush()
        try:
            r = subprocess.run(
                ['curl', '-s', '--max-time', '10', '-b', COOKIES_PATH, node['url']],
                capture_output=True, timeout=15
            )
            if r.returncode != 0:
                continue
            html = r.stdout.decode('utf-8', errors='replace')
            soup = BeautifulSoup(html, 'html.parser')
            # Eliminar navegación/estructura
            for tag in soup.find_all(['script','style','nav','header','footer']):
                tag.decompose()
            # Extraer contenido principal
            main = soup.find('main') or soup.find('article') or soup.find(id=re.compile(r'content|main', re.I)) or soup.body
            if main:
                node['content_full'] = ' '.join(main.get_text(' ', strip=True).split())
            enriched += 1
        except Exception:
            pass
    print(f"\n  Enriquecidas: {enriched}/{total_pages} páginas")

# ── 7. Escribir web-map-filtered.jsonl ───────────────────────────────────────
with open(FILTERED_PATH, 'w', encoding='utf-8') as f:
    for nid in node_order:
        if nid in included_all:
            f.write(json.dumps(nodes[nid], ensure_ascii=False) + '\n')

print(f"  Filtrado escrito → {FILTERED_PATH}")

# ── 8. Añadir exclusiones al fichero existente ────────────────────────────────
with open(EXCLUDED_PATH, 'a', encoding='utf-8') as f:
    for nid in node_order:
        if nid not in included_all:
            node = nodes[nid]
            record = {
                'url': node['url'],
                'depth': node.get('depth', 0),
                'excluded_reason': 'filter_topic'
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

print(f"  Exclusiones añadidas → {EXCLUDED_PATH}")

# ── 9. Actualizar scrapper-config.json ────────────────────────────────────────
now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
config['session']['filter_status']    = 'ok'
config['session']['filter_timestamp'] = now
config['metrics']['pages_included']   = len(included_page_ids)
config['metrics']['files_included']   = len(included_file_ids)
config['metrics']['filter_excluded']  = excluded_cnt

with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

# ── Resumen ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print(f"  RESUMEN DE FILTRADO")
print(f"{'═'*60}")
print(f"  Nodos totales en web-map:       {len(nodes)}")
print(f"  Páginas incluidas:              {len(included_page_ids)}")
print(f"  Ficheros incluidos:             {len(included_file_ids)}")
print(f"  Total incluidos:                {len(included_all)}")
print(f"  Excluidos (filtro tópico):      {excluded_cnt}")
print(f"{'═'*60}")
print(f"  web-map-filtered → {FILTERED_PATH}")
print(f"{'═'*60}\n")
