---
name: update
description: Updates plugin metadata (description, status, version bump) and propagates changes to all catalogs and the CLI cache. Also invoked explicitly as /p4-plugin:update with the plugin name.
version: 32
argument-hint: "<plugin>"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Plugin Updater

Updates plugin metadata and propagates changes to all catalogs and the CLI cache.

```
specs/catalog.json                                    ← PRIMARY — written first
   ↓
plugins/<plugin>/.claude-plugin/plugin.json        ← version if bumped
.claude-plugin/marketplace.json                       ← description/skills if changed
plugins/README.md                             ← description/status/skills if changed
README.md                                             ← status column if plugin status changed
~/.claude/plugins/cache/plugin4ai/         ← CLI cache (if version changed)
```

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
X, Y, Z = map(int, plugin["version"].split("."))
```

Show the user the current values before asking what to change.

---

## Step 2 — Collect changes

Use **AskUserQuestion** to collect what needs updating:

1. New description (leave blank to keep current)
2. New status (`proposal` / `accepted` / `beta` / `stable` / `production` / `deprecated`)
3. Version bump type (`none` / `patch X.Y+1.Z` / `major X+1.0.Z`) — Z is never reset manually
4. Changelog entry description (required if any change is made)

---

## Step 3 — Update catalog.json

Apply all collected changes:
- Update `description`, `status`, `version` as needed
- Prepend to `changelog`: `{"version": "X.Y.Z", "changes": "<description>"}`

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

Apply updates to all files affected by the collected changes. Check each trigger independently:

### Claude Code files (always applicable)

- `plugins/<plugin>/.claude-plugin/plugin.json` → update `version` if bumped
- `.claude-plugin/marketplace.json` → update `description` if changed; update skill list in `source` entry if skills changed
- `plugins/README.md` → update `status` column if status changed; update `Skills` column if skills changed; update `Auto-setup` column if agent was added/removed

### Root documentation

- `README.md` (repo root) → update `status` column in the plugins table if plugin status changed. If missing, insert in alphabetical order following `create` Step 7b.

---

## Step 5 — Sync cache (only if version bumped)

```python
import shutil, os, json

plugin_dir = f"{REPO_ROOT}/plugins/{plugin_name}"
version = json.load(open(f"{plugin_dir}/.claude-plugin/plugin.json"))["version"]
cache_base = os.path.expanduser(f"~/.claude/plugins/cache/plugin4ai/{plugin_name}")
os.makedirs(cache_base, exist_ok=True)
for old in os.listdir(cache_base): shutil.rmtree(f"{cache_base}/{old}")
dst = f"{cache_base}/{version}"
shutil.copytree(plugin_dir, dst, ignore=shutil.ignore_patterns('.git'))
for item in os.listdir(plugin_dir):
    if item.startswith('.') and item != '.git':
        s, d = f"{plugin_dir}/{item}", f"{dst}/{item}"
        if os.path.isdir(s):
            if os.path.exists(d): shutil.rmtree(d)
            shutil.copytree(s, d)
```

---

## Summary output

```
✅ Plugin updated: <plugin> v<old> → v<new>

Changes applied:
  <list of what changed>

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)
  [.claude-plugin/marketplace.json — if description/skills changed]
  [plugins/README.md — if description/status/skills changed]
  [README.md — if status changed]

[Cache synced: ~/.claude/plugins/cache/plugin4ai/<plugin>/<version>/]

Next steps:
  1. git add + commit + push
  2. claude plugins update <plugin>   (other consoles)
```
