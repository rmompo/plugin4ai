---
name: skill-add
description: Adds a new skill to an existing Codex CLI plugin. Creates the SKILL.md, increments the Z version counter in catalog.json, and updates plugin.json and README.md. Also invoked explicitly as /p4-plugin:skill-add with plugin and skill name.
---

# Skill Adder (Codex CLI)

Adds a new skill to an existing plugin. Z increments globally — it is the highest skill version ever assigned across all skills in any plugin.

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
X, Y, Z = map(int, plugin_entry["version"].split("."))
```

---

## Step 2 — Collect skill info via AskUserQuestion

Ask the user for:
1. Skill name (kebab-case)
2. Short description for the skill

---

## Step 3 — Validate

- Skill name must be kebab-case
- Skill must not already exist in `plugin_entry["skills"]`
- Plugin must exist in catalog

---

## Step 4 — Compute new Z

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

## Step 5 — Create skill file

### `codex/<plugin>/skills/<skill>/SKILL.md`

```markdown
---
name: <skill>
description: <skill description>
---

# <Skill Title>

TODO: Add skill instructions here.
```

---

## Step 6 — Update catalog.json

```python
plugin_entry["skills"].append({
    "name": skill_name,
    "version": new_skill_version,
    "description": skill_description
})
plugin_entry["version"] = new_plugin_version
plugin_entry["changelog"].insert(0, {
    "version": new_plugin_version,
    "changes": f"Add {skill_name} skill"
})
open(catalog_path, 'w').write(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 6b — Sync catalog to ~/.p4/

```python
import shutil, os
os.makedirs(os.path.expanduser("~/.p4"), exist_ok=True)
shutil.copy2(catalog_path, os.path.expanduser("~/.p4/catalog.json"))
```

---

## Step 7 — Update plugin.json

```python
plugin_json_path = f"{REPO_ROOT}/codex/{plugin_name}/plugin.json"
pj = json.load(open(plugin_json_path))
pj["version"] = new_plugin_version
open(plugin_json_path, 'w').write(json.dumps(pj, indent=2, ensure_ascii=False) + '\n')
```

---

## Step 8 — Update README.md

Add a row to the skills table in `codex/<plugin>/README.md`.

---

## Summary output

```
✅ Skill added: /<plugin>:<skill>

Plugin <plugin>: v<old> → v<new_plugin_version>
Skill version:  1.0.<new_z>

Files created:
  codex/<plugin>/skills/<skill>/SKILL.md

Updated:
  codex/<plugin>/plugin.json
  codex/<plugin>/README.md

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. Edit codex/<plugin>/skills/<skill>/SKILL.md with skill instructions
  2. codex /plugins → update <plugin>
  3. git add + commit + push
```
