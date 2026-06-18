---
name: skill-update
description: Updates the content of a skill and bumps the Z version counter in catalog.json and plugin.json. Also invoked explicitly as /p4-plugin:skill-update with plugin and skill name.
---

# Skill Updater (GitHub Copilot)

Updates skill content and bumps Z globally. The skill's `description` in catalog.json may also be updated.

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
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)
skill_entry = next((s for s in plugin_entry["skills"] if s["name"] == skill_name), None)
X, Y, Z = map(int, plugin_entry["version"].split("."))
```

If skill not found → report and exit.

---

## Step 2 — Collect changes via AskUserQuestion

Ask the user:
1. New skill description (leave blank to keep current)
2. Changelog description for this update

---

## Step 3 — Compute new Z

```python
global_max_z = max(
    int(p["version"].split(".")[2])
    for p in catalog["plugins"]
    if "version" in p
)
new_z = global_max_z + 1
new_skill_version = f"1.0.{new_z}"
new_plugin_version = f"{X}.{Y}.{new_z}"
```

---

## Step 4 — Update catalog.json

```python
skill_entry["version"] = new_skill_version
if new_description:
    skill_entry["description"] = new_description
plugin_entry["version"] = new_plugin_version
plugin_entry["changelog"].insert(0, {
    "version": new_plugin_version,
    "changes": changelog_description
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
plugin_json_path = f"{REPO_ROOT}/ghcopilot/plugins/{plugin_name}/plugin.json"
pj = json.load(open(plugin_json_path))
pj["version"] = new_plugin_version
open(plugin_json_path, 'w').write(json.dumps(pj, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 6 — Update SKILL.md description (if changed)

If the description was updated, edit the `description:` line in the SKILL.md frontmatter:

```
ghcopilot/plugins/<plugin>/skills/<skill>/SKILL.md
```

---

## Summary output

```
✅ Skill updated: /<plugin>:<skill>

Plugin <plugin>: v<old> → v<new>
Skill version:   1.0.<old_z> → 1.0.<new_z>

Updated:
  ghcopilot/plugins/<plugin>/skills/<skill>/SKILL.md
  ghcopilot/plugins/<plugin>/plugin.json

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. git add + commit + push
```
