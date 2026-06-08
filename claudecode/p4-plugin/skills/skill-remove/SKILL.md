---
name: skill-remove
description: Removes a skill from a plugin. Deletes the SKILL.md, updates catalog.json (Z does not decrease), and syncs the CLI cache. Destructive — requires explicit confirmation. Also invoked explicitly as /p4-plugin:skill-remove with the plugin and skill name.
version: 20
argument-hint: "<plugin> <skill>"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Skill Remover

Removes a skill from a plugin. **Destructive — the skill directory is deleted.**

Z does **not** decrease on removal — the counter is monotonic.

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
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)
skill_entry = next((s for s in plugin_entry["skills"] if s["name"] == skill_name), None)
```

If skill not found → report and exit.

---

## Step 2 — Confirm via AskUserQuestion

Use **AskUserQuestion**:
- question: `"¿Confirmas la eliminación del skill <skill> de <plugin>? Esta acción no se puede deshacer."`
- header: `"Confirmar"`
- options: `["Sí, eliminar", "Cancelar"]`

Only proceed if user confirms. On cancel → exit immediately.

---

## Step 3 — Delete skill directory

```bash
rm -rf REPO_ROOT/claudecode/<plugin>/skills/<skill>/
```

---

## Step 4 — Update catalog.json

Z does NOT change. Only remove the skill entry and record a changelog:

```python
import json
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
catalog = json.load(open(catalog_path))
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)

# Remove skill
plugin_entry["skills"] = [s for s in plugin_entry["skills"] if s["name"] != skill_name]

# Record in plugin changelog (version unchanged)
current_version = plugin_entry["version"]
plugin_entry["changelog"].insert(0, {
    "version": current_version,
    "changes": f"Remove {skill_name} skill"
})

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

## Step 4c — Update README.md

Use the Edit tool to remove the row for `<skill>` from the skills table in `REPO_ROOT/claudecode/<plugin>/README.md`.

Find the row matching the skill name and delete it. If no skills table exists or the skill is not listed, skip silently.

---

## Step 5 — Sync cache (no version bump)

```python
import shutil, os, json

plugin_dir = f"{REPO_ROOT}/claudecode/{plugin_name}"
version = json.load(open(f"{plugin_dir}/.claude-plugin/plugin.json"))["version"]
cache_base = os.path.expanduser(f"~/.claude/plugins/cache/plugin4ai-claudecode/{plugin_name}")
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
✅ Skill removed: /<plugin>:<skill>

Plugin <plugin>: v<version> (Z unchanged — removal does not bump Z)

Deleted:
  claudecode/<plugin>/skills/<skill>/

Updated:
  claudecode/<plugin>/README.md

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Cache synced: ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/<version>/

Next steps:
  1. git add + commit + push
  2. claude plugins update <plugin>
```
