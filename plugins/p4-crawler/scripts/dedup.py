#!/usr/bin/env python3
# ---
# version: 1.1
# description: Deduplicación del web-map — COMMAND-4-DEDUP
# agent: doc-scrapper
# author: rmompo@gmail.com
# created: 2026-02-24T00:00:00
# updated: 2026-03-09T00:00:00
# ---

import json, datetime, sys, os

DEFAULT_CONFIG = "generated/scrapp/mova3/data/scrapper-config.json"
CONFIG_PATH    = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG

with open(CONFIG_PATH, encoding='utf-8') as f:
    _cfg = json.load(f)

_folder           = _cfg["output"]["folder"]
_data             = os.path.join(_folder, "data")
WEBMAP_META_PATH  = os.path.join(_data, "web-map-meta.json")
WEBMAP_NODES_PATH = os.path.join(_data, "web-map-nodes.jsonl")
EXCLUDED_PATH     = os.path.join(_data, "web-map-excluded.jsonl")

print(f"\n{'═'*55}")
print(f"  COMMAND-3.2-DEDUP — Deduplicación del web-map")
print(f"{'═'*55}\n")

# ── 1. Cargar todos los nodos ─────────────────────────────────────────────────
nodes      = {}   # {id: node}
node_order = []   # orden de inserción

with open(WEBMAP_NODES_PATH, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        node = json.loads(line)
        nodes[node['id']] = node
        node_order.append(node['id'])

print(f"  Nodos cargados: {len(node_order)}")

# ── 2. Detectar ficheros duplicados por URL ───────────────────────────────────
url_to_canonical = {}   # url -> id canónico (primer nodo visto)
id_remap         = {}   # id_duplicado -> id_canónico
duplicate_ids    = set()

for nid in node_order:
    node = nodes[nid]
    if node['type'] != 'file':
        continue
    url = node['url']
    if url in url_to_canonical:
        id_remap[nid] = url_to_canonical[url]
        duplicate_ids.add(nid)
    else:
        url_to_canonical[url] = nid

print(f"  Ficheros duplicados detectados: {len(duplicate_ids)}")

# ── 3. Actualizar links en todos los nodos ────────────────────────────────────
for node in nodes.values():
    if not node.get('links'):
        continue
    resolved = [id_remap.get(lid, lid) for lid in node['links']]
    # Eliminar duplicados manteniendo orden y excluyendo IDs eliminados
    seen, clean = set(), []
    for lid in resolved:
        if lid not in seen and lid not in duplicate_ids:
            seen.add(lid)
            clean.append(lid)
    node['links'] = clean

# ── 4. Reescribir JSONL sin duplicados ───────────────────────────────────────
kept = 0
with open(WEBMAP_NODES_PATH, 'w', encoding='utf-8') as f:
    for nid in node_order:
        if nid not in duplicate_ids:
            f.write(json.dumps(nodes[nid], ensure_ascii=False) + '\n')
            kept += 1

print(f"  Nodos escritos (sin duplicados): {kept}")

# ── 5. Registrar duplicados en excluded ──────────────────────────────────────
if duplicate_ids:
    with open(EXCLUDED_PATH, 'a', encoding='utf-8') as f:
        for nid in duplicate_ids:
            node = nodes[nid]
            record = {
                'url': node['url'],
                'depth': node['depth'],
                'excluded_reason': f'duplicate_file (canonical: {id_remap[nid]})'
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

# ── 6. Actualizar web-map-meta.json ──────────────────────────────────────────
with open(WEBMAP_META_PATH, encoding='utf-8') as f:
    meta = json.load(f)

pages = sum(1 for nid, n in nodes.items() if n['type'] == 'page' and nid not in duplicate_ids)
files = sum(1 for nid, n in nodes.items() if n['type'] == 'file' and nid not in duplicate_ids)

meta['url_index']       = {n['url']: nid for nid, n in nodes.items() if nid not in duplicate_ids}
meta['stats']['pages']  = pages
meta['stats']['files']  = files
meta['stats']['excluded'] = meta['stats'].get('excluded', 0) + len(duplicate_ids)
meta['dedup_status']    = 'done'
meta['updated']         = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

with open(WEBMAP_META_PATH, 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

# ── Resumen ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*55}")
print(f"  RESUMEN DEDUP")
print(f"{'═'*55}")
print(f"  Nodos originales:        {len(node_order)}")
print(f"  Ficheros duplicados:     {len(duplicate_ids)}")
print(f"  Nodos finales:           {kept}")
print(f"  Páginas:                 {pages}")
print(f"  Ficheros únicos:         {files}")
print(f"{'═'*55}\n")
print(f"  web-map-nodes   → {WEBMAP_NODES_PATH}")
print(f"  web-map-meta    → {WEBMAP_META_PATH}")
print(f"{'═'*55}\n")
