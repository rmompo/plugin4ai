---
name: skill-update
description: Bumps the version of an existing skill, records the changelog entry in catalog.json, and syncs the CLI cache. Also invoked explicitly as /p4-plugin:skill-update with the plugin and skill name.
version: 8
argument-hint: "<plugin> <skill>"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Skill Updater

Bumps the skill version (Z+1), records the change in catalog.json, and syncs the CLI cache.

---

## Z versioning rules

- `new_Z = current_Z + 1`
- Skill `version` → `new_Z`
- Plugin `Z` → `new_Z`
- Z is monotonic — never resets

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
skill_entry = next(s for s in plugin_entry["skills"] if s["name"] == skill_name)

X, Y, Z = map(int, plugin_entry["version"].split("."))
new_Z = Z + 1
new_version = f"{X}.{Y}.{new_Z}"
```

---

## Step 2 — Collect change description

Use **AskUserQuestion**:
- question: `"Describe el cambio realizado en el skill <skill> (una línea)"`
- header: `"Changelog"`
- options: free text (use Other)

---

## Step 3 — Update SKILL.md frontmatter

Read `REPO_ROOT/claudecode/<plugin>/skills/<skill>/SKILL.md` and update:

```
version: <old_Z>  →  version: <new_Z>
```

---

## Step 4 — Update catalog.json

```python
import json
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
catalog = json.load(open(catalog_path))
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)
skill_entry = next(s for s in plugin_entry["skills"] if s["name"] == skill_name)

# Update skill
skill_entry["version"] = new_Z
skill_entry["changelog"].insert(0, {"version": new_Z, "changes": change_description})

# Bump plugin version
plugin_entry["version"] = new_version
plugin_entry["changelog"].insert(0, {
    "version": new_version,
    "changes": f"{skill_name}: {change_description}"
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

## Step 5 — Update plugin.json

```python
pj_path = f"{REPO_ROOT}/claudecode/{plugin_name}/.claude-plugin/plugin.json"
pj = json.load(open(pj_path))
pj["version"] = new_version
open(pj_path, 'w').write(json.dumps(pj, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 6 — Sync cache

```python
import shutil, os

plugin_dir = f"{REPO_ROOT}/claudecode/{plugin_name}"
cache_base = os.path.expanduser(f"~/.claude/plugins/cache/plugin4ai-claudecode/{plugin_name}")
os.makedirs(cache_base, exist_ok=True)
for old in os.listdir(cache_base): shutil.rmtree(f"{cache_base}/{old}")
dst = f"{cache_base}/{new_version}"
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
✅ Skill updated: /<plugin>:<skill> v<old_Z> → v<new_Z>

Plugin <plugin>: v<old_version> → v<new_version>

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Files updated:
  claudecode/<plugin>/skills/<skill>/SKILL.md

Cache synced: ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/<new_version>/

Next steps:
  1. git add + commit + push
  2. claude plugins update <plugin>
```
