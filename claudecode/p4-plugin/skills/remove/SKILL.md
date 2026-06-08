---
name: remove
description: Removes a plugin and all its files from the repo, every catalog, and the CLI cache. Destructive — requires explicit confirmation. Also invoked explicitly as /p4-plugin:remove with the plugin name.
version: 6
argument-hint: "<plugin>"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Plugin Remover

Removes a plugin completely — all files, all catalog entries, CLI cache. **Destructive and irreversible.**

---

## Step 0 — Locate repo root

```bash
find ~ -name "marketplace.json" -path "*plugin4ai*/.claude-plugin*" 2>/dev/null | head -1
# REPO_ROOT = two levels up from result
```

---

## Step 1 — Read current state

```python
import json
catalog = json.load(open(f"{REPO_ROOT}/specs/catalog.json"))
plugin = next((p for p in catalog["plugins"] if p["name"] == plugin_name), None)
```

If plugin not found in catalog → report and exit.

---

## Step 2 — Confirm via AskUserQuestion

List exactly what will be permanently deleted:

```
⚠️  This will permanently delete:

  claudecode/<plugin>/           (plugin directory and all skills)
  specs/<plugin>.md              (plugin spec)

  Entries removed from:
  specs/catalog.json
  .claude-plugin/marketplace.json
  claudecode/MARKETPLACE.md
  ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/

This action cannot be undone.
```

Use **AskUserQuestion**:
- question: `"¿Confirmas la eliminación de <plugin> y todos sus ficheros?"`
- options: `["Sí, eliminar", "Cancelar"]`

Only proceed if user confirms. On cancel → exit immediately.

---

## Step 3 — Delete plugin files

```bash
rm -rf REPO_ROOT/claudecode/<plugin>/
rm -f REPO_ROOT/specs/<plugin>.md
```

---

## Step 4 — Remove from catalog.json

```python
import json
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
catalog = json.load(open(catalog_path))
catalog["plugins"] = [p for p in catalog["plugins"] if p["name"] != plugin_name]
open(catalog_path, 'w').write(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 4b — Sync catalog to ~/.p4/

```python
import shutil, os
os.makedirs(os.path.expanduser("~/.p4"), exist_ok=True)
shutil.copy2(catalog_path, os.path.expanduser("~/.p4/catalog.json"))
```

---

## Step 5 — Remove from .claude-plugin/marketplace.json

```python
import json
mp_path = f"{REPO_ROOT}/.claude-plugin/marketplace.json"
mp = json.load(open(mp_path))
mp["plugins"] = [p for p in mp["plugins"] if p["name"] != plugin_name]
open(mp_path, 'w').write(json.dumps(mp, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 6 — Remove row from claudecode/MARKETPLACE.md

Remove the line containing `[`<plugin>`]` from the Available plugins table.

---

## Step 7 — Remove cache

```python
import shutil, os
cache_dir = os.path.expanduser(f"~/.claude/plugins/cache/plugin4ai-claudecode/{plugin_name}")
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
```

---

## Summary output

```
✅ Plugin removed: <plugin>

Deleted:
  claudecode/<plugin>/
  specs/<plugin>.md
  Cache: ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/

Removed from:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)
  .claude-plugin/marketplace.json
  claudecode/MARKETPLACE.md

Next steps:
  1. git add + commit + push
```
