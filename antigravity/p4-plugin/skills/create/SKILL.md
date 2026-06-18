---
name: create
description: Scaffolds a new Antigravity CLI plugin with an initial skill, spec file, and catalog entry. Also invoked explicitly as /p4-plugin:create with the plugin name.
---

# Plugin Creator (Antigravity CLI)

Scaffolds a complete new plugin in the `antigravity/` directory and registers it in the catalog.

```
antigravity/<plugin>/
├── plugin.json
├── README.md
└── skills/
    └── <initial-skill>/
        └── SKILL.md
specs/<plugin>.md
specs/catalog.json   ← plugin entry added
```

---

## Step 0 — Locate repo root

```bash
git rev-parse --show-toplevel 2>/dev/null
```

---

## Step 1 — Collect plugin info via AskUserQuestion

Ask the user for:
1. Plugin name (kebab-case, no spaces)
2. Short description (one sentence)
3. Name of the first skill to scaffold
4. Short description of the first skill

---

## Step 2 — Validate

- Plugin name must be kebab-case (`[a-z0-9-]+`)
- Plugin must not already exist in `specs/catalog.json`
- Skill name must be kebab-case

Abort with a clear error if any check fails.

---

## Step 3 — Read current catalog Z counter

```python
import json
catalog = json.load(open(f"{REPO_ROOT}/specs/catalog.json"))
# Find current max Z across all plugins
max_z = max(
    int(p["version"].split(".")[2])
    for p in catalog["plugins"]
    if "version" in p
)
new_z = max_z + 1
new_version = f"1.0.{new_z}"
```

---

## Step 4 — Create plugin directory and files

### `antigravity/<plugin>/plugin.json`

```json
{
  "name": "<plugin>",
  "version": "1.0.<Z>",
  "description": "<description>",
  "author": {
    "name": "<git config user.name>",
    "email": "<git config user.email>"
  }
}
```

### `antigravity/<plugin>/skills/<skill>/SKILL.md`

```markdown
---
name: <skill>
description: <skill description>
---

# <Skill Title>

TODO: Add skill instructions here.
```

### `antigravity/<plugin>/README.md`

```markdown
# <plugin>

<description>

## Skills

| Skill | Invocation | Description |
|-------|------------|-------------|
| `<skill>` | `/<plugin>:<skill>` | <skill description> |

## Installation

\`\`\`bash
agy plugin install ~/path/to/plugin4ai/antigravity/<plugin>
\`\`\`
```

---

## Step 5 — Create spec file `specs/<plugin>.md`

```markdown
# <plugin>

<description>

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| `<skill>` | 1.0.<Z> | <skill description> |

## Ports

| CLI | Status | Path |
|-----|--------|------|
| Antigravity CLI | beta | `antigravity/<plugin>` |

## Changelog

### 1.0.<Z>
- Initial release
```

---

## Step 6 — Add entry to `specs/catalog.json`

Add to the `plugins` array:

```json
{
  "name": "<plugin>",
  "description": "<description>",
  "version": "1.0.<Z>",
  "status": "beta",
  "skills": [
    { "name": "<skill>", "version": "1.0.<Z>", "description": "<skill description>" }
  ],
  "ports": {
    "claudecode": { "status": "not-applicable" },
    "ghcopilot": { "status": "not-applicable" },
    "antigravity": { "status": "beta", "path": "antigravity/<plugin>" },
    "codex": { "status": "not-applicable" }
  },
  "dependencies": [],
  "changelog": [
    { "version": "1.0.<Z>", "changes": "Initial release" }
  ]
}
```

---

## Step 6b — Sync catalog to ~/.p4/

```python
import shutil, os
catalog_path = f"{REPO_ROOT}/specs/catalog.json"
os.makedirs(os.path.expanduser("~/.p4"), exist_ok=True)
shutil.copy2(catalog_path, os.path.expanduser("~/.p4/catalog.json"))
```

---

## Summary output

```
✅ Plugin created: <plugin> v1.0.<Z>

Files created:
  antigravity/<plugin>/plugin.json
  antigravity/<plugin>/skills/<skill>/SKILL.md
  antigravity/<plugin>/README.md
  specs/<plugin>.md

Catalog updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)

Next steps:
  1. Edit antigravity/<plugin>/skills/<skill>/SKILL.md with skill instructions
  2. agy plugin install ~/path/to/plugin4ai/antigravity/<plugin>
  3. git add + commit + push
```
