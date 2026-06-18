---
name: skill-remove
description: Removes a skill from a plugin. Deletes the SKILL.md and updates catalog.json. Z does not decrease. Destructive — requires explicit confirmation. Also invoked explicitly as /p4-plugin:skill-remove with plugin and skill name.
---

# Skill Remover (Codex CLI)

Removes a skill from a plugin. **Destructive — the skill directory is deleted.**

Z does **not** decrease on removal — the counter is monotonic.

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
rm -rf REPO_ROOT/codex/<plugin>/skills/<skill>/
```

---

## Step 4 — Update catalog.json

Z does NOT change. Only remove the skill entry and record a changelog:

```python
plugin_entry["skills"] = [s for s in plugin_entry["skills"] if s["name"] != skill_name]
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

## Step 5 — Update README.md

Remove the row for `<skill>` from the skills table in `codex/<plugin>/README.md`.

---

## Summary output

```
✅ Skill removed: /<plugin>:<skill>

Plugin <plugin>: v<version> (Z unchanged — removal does not bump Z)

Deleted:
  codex/<plugin>/skills/<skill>/

Updated:
  codex/<plugin>/README.md

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. git add + commit + push
  2. codex /plugins → update <plugin>
```
