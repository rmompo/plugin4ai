---
name: update
description: Updates plugin metadata (description, status, ports, version bump) and propagates changes to all catalogs. Also invoked explicitly as /p4-plugin:update with the plugin name.
---

# Plugin Updater (GitHub Copilot)

Updates plugin metadata and propagates changes to all catalogs.

```
specs/catalog.json                              ← PRIMARY — written first
   ↓
ghcopilot/plugins/<plugin>/plugin.json          ← version if bumped
```

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
X, Y, Z = map(int, plugin["version"].split("."))
```

Show the user the current values before asking what to change.

---

## Step 2 — Collect changes

Use **AskUserQuestion** to collect what needs updating:

1. New description (leave blank to keep current)
2. New status (`proposal` / `accepted` / `beta` / `stable` / `production` / `deprecated`)
3. Version bump type (`none` / `patch X.Y+1.Z` / `major X+1.0.Z`) — Z is never reset manually
4. Port changes (add or update CLI port statuses)
5. Changelog entry description (required if any change is made)

---

## Step 3 — Update catalog.json

Apply all collected changes:
- Update `description`, `status`, `version` as needed
- Prepend to `changelog`: `{"version": "X.Y.Z", "changes": "<description>"}`
- Update `ports` if changed

---

## Step 3b — Sync catalog to ~/.p4/

```python
import shutil, os
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
os.makedirs(os.path.expanduser("~/.p4"), exist_ok=True)
shutil.copy2(catalog_path, os.path.expanduser("~/.p4/catalog.json"))
```

---

## Step 4 — Update derived files

- `ghcopilot/plugins/<plugin>/plugin.json` → update `version` if bumped

---

## Summary output

```
✅ Plugin updated: <plugin> v<old> → v<new>

Changes applied:
  <list of what changed>

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. git add + commit + push
```
