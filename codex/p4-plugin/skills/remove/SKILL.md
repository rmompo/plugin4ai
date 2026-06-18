---
name: remove
description: Removes a plugin and all its files from the repo and every catalog. Destructive — requires explicit confirmation. Also invoked explicitly as /p4-plugin:remove with the plugin name.
---

# Plugin Remover (Codex CLI)

Removes a plugin completely — all files and all catalog entries. **Destructive and irreversible.**

---

## Step 0 — Locate repo root

```bash
git rev-parse --show-toplevel 2>/dev/null
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

  codex/<plugin>/        (plugin directory and all skills)
  specs/<plugin>.md      (plugin spec)

  Entries removed from:
  specs/catalog.json

This action cannot be undone.
```

Use **AskUserQuestion**:
- question: `"¿Confirmas la eliminación de <plugin> y todos sus ficheros?"`
- options: `["Sí, eliminar", "Cancelar"]`

Only proceed if user confirms. On cancel → exit immediately.

---

## Step 3 — Delete plugin files

```bash
rm -rf REPO_ROOT/codex/<plugin>/
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

## Summary output

```
✅ Plugin removed: <plugin>

Deleted:
  codex/<plugin>/
  specs/<plugin>.md

Removed from:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. git add + commit + push
  2. Uninstall from Codex: remove ~/.codex/plugins/<plugin>/
```
