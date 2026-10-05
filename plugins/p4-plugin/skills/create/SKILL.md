---
name: create
description: Scaffolds a new plugin with all required files and registers it in every catalog. Also invoked explicitly as /p4-plugin:create with the plugin name and optional skill names.
version: 31
argument-hint: "<plugin> [skill1 skill2 ...]"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Plugin Creator

Scaffolds a complete new plugin and registers it in all catalogs and the Claude Code cache.

```
specs/catalog.json                              ← PRIMARY — written first
   ↓
plugins/<plugin>/.claude-plugin/plugin.json     ← minimal plugin metadata
.claude-plugin/marketplace.json                 ← Claude Code marketplace index
plugins/README.md                               ← human-readable plugin index
specs/<plugin>.md                               ← plugin spec file
~/.claude/plugins/cache/plugin4ai/   ← Claude Code cache
```

---

## Step 0 — Locate repo root

```bash
find ~ -name "marketplace.json" -path "*plugin4ai*/.claude-plugin*" 2>/dev/null | head -1
# REPO_ROOT = two levels up from result
```

---

## Step 1 — Collect info

If not provided as arguments, use **AskUserQuestion** to collect:

1. Plugin name (`p4-<descriptor>`, kebab-case)
2. Plugin description (one line)
3. Category (default: `productivity`)
4. Initial status (default: `beta`)
5. Scopes (optional — select from `global`, `local`, `local-gitignore`, or none)
6. Dependencies (optional):
   - **Tool dependencies** — binary name + version constraint. Operators: `=x.y.z`, `>=x.y.z`, `>x.y.z`, `<=x.y.z`, `<x.y.z`, `>=x.y.z <a.b.c`, `*`. Example: `pandoc >=2.0.0`, `python3 >=3.8.0`
   - **Plugin dependencies** — other plugin4ai plugins this plugin relies on. Example: `p4-converter`. No version — always latest.
7. Skill name(s) and brief purpose of each (optional — can add later with `skill-add`)
### Naming conventions

**Plugin:** `p4-{container}` — domain or category grouping related skills.

**Skill:** `[subject-]{action}` — action is mandatory, subject is optional.

**Invocation:** `/p4-{container}:[subject-]{action}`

### Setup skill convention

**If the plugin declares `dependencies`**, always scaffold a `setup` skill as the first skill (Z=1). The `setup` skill must:

1. Read the full `dependencies` array from `catalog.json` for this plugin
2. For each dependency, check by type:
   - `type: "tool"` → run `which <name> && <name> --version 2>&1 | head -1`, then compare version against constraint
   - `type: "plugin"` → run `ls ~/.claude/plugins/cache/plugin4ai/<name>/` — installed if directory has at least one entry
3. Print a unified Markdown table with a `Type` column:
   ```markdown
   | Type | Dependency | Required | Found | Status |
   |------|------------|----------|-------|--------|
   | tool | pandoc     | >=2.0.0  | 3.1.3 | ✅     |
   | plugin | p4-core  | —        | ✅    | ✅     |
   ```
   Status: ✅ if present (and version satisfied for tools), ❌ if missing
4. For each ❌, show install instructions:
   - `type: "tool"` — `apt`/`brew` (Bash) and `winget`/`choco` (PowerShell)
   - `type: "plugin"` — `claude plugins install <name>`
5. Be idempotent — safe to re-run at any time

---

## Step 2 — Assign versions

- Plugin starts at `1.0.0` (no skills) or `1.0.<N>` (N skills provided)
- First skill → Z=1, second → Z=2, etc.

---

## Step 3 — Create plugin files

Create `REPO_ROOT/plugins/<plugin>/`:

```
<plugin>/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── <skill>/
│       └── SKILL.md
└── README.md
```

If the plugin needs a session-start agent (auto-setup behavior), also create:
```
├── agents/
│   └── <plugin>.md
└── settings.json     ← {"agent": "<plugin>"}
```

**`.claude-plugin/plugin.json`** (minimal — all metadata lives in catalog.json):
```json
{
  "name": "<plugin>",
  "version": "1.0.<Z>",
  "description": "<one-line description>",
  "author": {
    "name": "rmompo",
    "email": "rmompo@gmail.com"
  },
  "scopes": ["<scope1>", "<scope2>"]   ← omit if no persistent storage needed
}
```

**`skills/<skill>/SKILL.md`**:
```markdown
---
name: <skill>
description: <what it does>. Also invoked explicitly as /<plugin>:<skill> with optional args.
version: <Z>
argument-hint: "[optional args]"
allowed-tools: [Bash, Read, Edit, Write]
---

# <Skill Title>

<Brief description.>

---

## TODO: define skill steps here
```

**`README.md`**:
```markdown
# <plugin>

<One paragraph description.>

## Skills

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| `<skill>` | `/<plugin>:<skill>` | <description> |

## Installation

\`\`\`bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install <plugin>
\`\`\`
```

---

## Step 4 — Create spec file

Create `REPO_ROOT/specs/<plugin>.md`:

```markdown
# Plugin Spec: <plugin>

> **Status:** `beta` | **Version:** `1.0.<Z>`

## Overview

<Description.>

---

## Skill: `<skill>`

### Purpose
<What it does.>

### Invocation
\`\`\`
/<plugin>:<skill> [args]
\`\`\`

### Non-Goals
- <What it does NOT do>

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.<Z> | Initial release |
```

---

## Step 5 — Update catalog.json

Add plugin entry:

```json
{
  "name": "<plugin>",
  "description": "<description>",
  "category": "<category>",
  "status": "<status>",
  "version": "1.0.<Z>",
  "spec": "specs/<plugin>.md",
  "path": "plugins/<plugin>",
  "scopes": ["<scope1>"],              ← omit if no persistent storage needed
  "dependencies": [                    ← omit if no dependencies needed
    {"type": "tool",   "name": "<binary>",  "version": "<constraint>"},
    {"type": "plugin", "name": "<plugin>"}
  ],
  "changelog": [
    {"version": "1.0.<Z>", "changes": "Initial release"}
  ],
  "skills": [
    {
      "name": "<skill>",
      "version": <Z>,
      "changelog": [{"version": <Z>, "changes": "Initial release"}]
    }
  ]
}
```

---

## Step 5b — Sync catalog to ~/.p4/

```python
import shutil, os
os.makedirs(os.path.expanduser("~/.p4"), exist_ok=True)
shutil.copy2(f"{REPO_ROOT}/specs/catalog.json", os.path.expanduser("~/.p4/catalog.json"))
```

---

## Step 7 — Update marketplace files

### 7.1 — `plugins/README.md`

Add row to the "Available plugins" table in alphabetical order:

```
| [`<plugin>`](./<plugin>/README.md) | <status> | `<skill1>`, `<skill2>` | <auto-setup> |
```

- `<status>`: from Step 1 (e.g. `beta`)
- Skills: comma-separated list of all implemented skills (exclude proposal)
- `<auto-setup>`: `✅ via agent` if the plugin has `settings.json` + `agents/<plugin>.md`; otherwise `—`

### 7.2 — `.claude-plugin/marketplace.json`

Add entry to the `"plugins"` array:

```json
{
  "name": "<plugin>",
  "description": "<description>",
  "author": {"name": "rmompo"},
  "category": "<category>",
  "source": "./plugins/<plugin>",
  "homepage": "https://github.com/rmompo/plugin4ai/tree/main/plugins/<plugin>"
}
```

---

## Step 7b — Update root README.md

Insert a row for the new plugin **in alphabetical order** in the plugins table of `REPO_ROOT/README.md` (columns `Plugin | Description | Status | Spec`):

```markdown
| `<plugin>` | <one-line description> | `<status>` | [spec](./specs/<plugin>.md) |
```

---

## Step 8 — Sync cache

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
✅ Plugin created: <plugin> v1.0.<Z>

Files created:
  plugins/<plugin>/.claude-plugin/plugin.json
  plugins/<plugin>/skills/<skill>/SKILL.md
  plugins/<plugin>/README.md
  specs/<plugin>.md

Marketplaces updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)
  .claude-plugin/marketplace.json
  plugins/README.md
  README.md  (plugins table — alphabetical)

Cache synced: ~/.claude/plugins/cache/plugin4ai/<plugin>/1.0.<Z>/

Next steps:
  1. Fill in skill logic in skills/<skill>/SKILL.md
  2. git add + commit + push
  3. claude plugins install <plugin>
```
