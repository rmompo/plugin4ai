---
name: skill-add
description: Adds a new skill to an existing plugin. Bumps Z versioning in catalog.json and plugin.json, creates the SKILL.md, and syncs the CLI cache. Also invoked explicitly as /p4-plugin:skill-add with the plugin and skill name.
version: 19
argument-hint: "<plugin> <skill>"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Skill Adder

Adds a new skill to an existing plugin, bumps Z versioning, and syncs all catalogs and the CLI cache.

---

## Z versioning rules

- `new_Z = current_Z + 1`
- New skill gets `version: new_Z`
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
plugin = next((p for p in catalog["plugins"] if p["name"] == plugin_name), None)
X, Y, Z = map(int, plugin["version"].split("."))
new_Z = Z + 1
new_version = f"{X}.{Y}.{new_Z}"
```

---

## Step 2 — Collect skill info

Use **AskUserQuestion** to collect:

1. Skill description (one line — also used in SKILL.md frontmatter)
2. `argument-hint` (optional, e.g. `"<plugin> [skill1 ...]"`)
3. `allowed-tools` (default: `[Bash, Read, Edit, Write]`)

---

## Step 3 — Create SKILL.md

Create `REPO_ROOT/claudecode/<plugin>/skills/<skill>/SKILL.md`:

```markdown
---
name: <skill>
description: <description>. Also invoked explicitly as /<plugin>:<skill> with optional args.
version: <new_Z>
argument-hint: "<argument-hint>"
allowed-tools: [<allowed-tools>]
---

# <Skill Title>

<Brief description.>

---

## TODO: define skill steps here
```

---

## Step 4 — Update catalog.json

```python
import json
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
catalog = json.load(open(catalog_path))
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)

# Add new skill
plugin_entry["skills"].append({
    "name": skill_name,
    "version": new_Z,
    "changelog": [{"version": new_Z, "changes": "Initial release"}]
})

# Bump plugin version
plugin_entry["version"] = new_version
plugin_entry["changelog"].insert(0, {
    "version": new_version,
    "changes": f"Add {skill_name} skill"
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

## Step 5b — Update README.md

Update `REPO_ROOT/claudecode/<plugin>/README.md` to include the new skill.

**If README.md does not exist**, create it using the Write tool:

```markdown
# <plugin>

<description from catalog — in English>

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `<skill>` | `/<plugin>:<skill>` | <first sentence of SKILL.md description> |

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install <plugin>
```
```

**If README.md exists**, use the Edit tool to insert a new row into the skills table:

```markdown
| `<skill>` | `/<plugin>:<skill>` | <first sentence of SKILL.md description> |
```

Insert before the closing blank line of the table. All content must be in English.

---

## Step 6 — Sync cache

```python
import shutil, os, json

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
✅ Skill added: /<plugin>:<skill> (v<new_Z>)

Plugin <plugin>: v<old_version> → v<new_version>

Files created/updated:
  claudecode/<plugin>/skills/<skill>/SKILL.md
  claudecode/<plugin>/README.md

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Cache synced: ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/<new_version>/

Next steps:
  1. Fill in skill logic in skills/<skill>/SKILL.md
  2. git add + commit + push
  3. claude plugins update <plugin>
```
