---
name: create
description: Scaffolds a new plugin with all required files and registers it in every catalog. Also invoked explicitly as /p4-plugin:create with the plugin name and optional skill names.
version: 29
argument-hint: "<plugin> [skill1 skill2 ...]"
allowed-tools: [Bash, Read, Edit, Write, AskUserQuestion]
---

# Plugin Creator

Scaffolds a complete new plugin and registers it in all catalogs and the CLI cache.

```
specs/catalog.json                              ← PRIMARY — written first
   ↓
claudecode/<plugin>/.claude-plugin/plugin.json  ← minimal CLI metadata
.claude-plugin/marketplace.json                 ← Claude Code marketplace index
claudecode/MARKETPLACE.md                       ← Claude Code human-readable catalog
specs/<plugin>.md                               ← plugin spec file
~/.claude/plugins/cache/plugin4ai-claudecode/   ← CLI cache
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
8. **Port decisions** — for each supported CLI/TUI, decide the status using **AskUserQuestion** (multiSelect allowed):

   | CLI | Options |
   |-----|---------|
   | `claudecode` | `beta` / `stable` (always implemented — the primary port) |
   | `ghcopilot` | `beta` / `stable` / `proposal` / `not-available` |
   | `antigravity` | `beta` / `stable` / `proposal` / `not-available` |
   | `codex` | `beta` / `stable` / `proposal` / `not-available` |

   - **`beta` / `stable`**: will be scaffolded and registered in this operation.
   - **`proposal`**: recorded in `catalog.json` and `specs/<plugin>.md` as planned, but no files created.
   - **`not-available`**: explicitly excluded — recorded in `catalog.json` with `"status": "not-available"`.

   For any port set to `beta`/`stable`, ask which skills from the initial skill list should be included in that port (some skills may be CLI-exclusive).

### Naming conventions

**Plugin:** `p4-{container}` — domain or category grouping related skills.

**Skill:** `[subject-]{action}` — action is mandatory, subject is optional.

**Invocation:** `/p4-{container}:[subject-]{action}`

### Setup skill convention

**If the plugin declares `dependencies`**, always scaffold a `setup` skill as the first skill (Z=1). The `setup` skill must:

1. Read the full `dependencies` array from `catalog.json` for this plugin
2. For each dependency, check by type:
   - `type: "tool"` → run `which <name> && <name> --version 2>&1 | head -1`, then compare version against constraint
   - `type: "plugin"` → run `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/` — installed if directory has at least one entry
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

Create `REPO_ROOT/claudecode/<plugin>/`:

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

> **Status:** `beta` | **Version:** `1.0.<Z>` | **Ports:** Claude Code only

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

## Port Status

| CLI | Location | Status | Notes |
|-----|----------|--------|-------|
| Claude Code | `claudecode/<plugin>/` | ✅ Beta | <skills included> |
| GitHub Copilot | `ghcopilot/plugins/<plugin>/` | <status> | <notes or —> |
| Antigravity | `antigravity/<plugin>/` | <status> | <notes or —> |
| Codex | `codex/<plugin>/` | <status> | <notes or —> |

Replace each `<status>` with: ✅ Beta / ✅ Stable / 🔲 Proposal / ❌ Not available — based on port decisions collected in Step 1.

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
  ],
  "ports": {
    "claudecode": {"status": "beta", "path": "claudecode/<plugin>"},
    "ghcopilot": {
      "status": "<decided-status>",
      "path": "ghcopilot/plugins/<plugin>",          ← only if beta/stable
      "notes": "<excluded skills if any>"             ← only if applicable
    },
    "antigravity": {"status": "<decided-status>"},   ← add path only if beta/stable
    "codex":       {"status": "<decided-status>"}    ← add path only if beta/stable
  }
  // Omit path and notes for proposal/not-available ports
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

## Step 6 — Update .claude-plugin/marketplace.json

Add to the `"plugins"` array:

```json
{
  "name": "<plugin>",
  "description": "<description>",
  "author": {"name": "rmompo"},
  "category": "productivity",
  "source": "./claudecode/<plugin>",
  "homepage": "https://github.com/rmompo/plugin4ai/tree/main/claudecode/<plugin>"
}
```

---

## Step 7 — Update claudecode/MARKETPLACE.md

Add row to the "Available plugins" table:

```
| [`<plugin>`](./<plugin>/README.md) | beta | `<skill>` | — |
```

---

## Step 7b — Update root README.md

The plugins table in `REPO_ROOT/README.md` is split into two groups. Determine which group the new plugin belongs to, then insert its row in alphabetical order within that group.

### Plugin groups

**Group 1 — General plugins** (cross-CLI, not tied to a specific CLI/TUI):
- Any plugin whose name does NOT include a CLI/TUI identifier.
- Table columns: `Plugin | Description | Status | Spec`
- Row format:
```markdown
| `<plugin>` | <one-line description> | `<status>` | [spec](./specs/<plugin>.md) |
```

**Group 2 — CLI/TUI-specific plugins** (exclusively for one CLI/TUI):
- Plugins whose name contains a CLI identifier: `antigravity`, `claudecode`, `copilot`, `codex`, or similar.
- Table columns: `Plugin | CLI/TUI | Description | Status | Spec`
- Row format:
```markdown
| `<plugin>` | <CLI/TUI name> | <one-line description> | `<status>` | [spec](./specs/<plugin>.md) |
```

### Insertion rule

Insert the new row **in alphabetical order** within the correct group. Do not append at the end — find the correct alphabetical position.

---

## Step 7c — Scaffold non-claudecode ports (if beta/stable)

For each port decided as `beta` or `stable` in Step 1 (except `claudecode`):

### GitHub Copilot port

If `ghcopilot` → `beta`/`stable`:

1. Create `REPO_ROOT/ghcopilot/plugins/<plugin>/plugin.json`:
```json
{
  "name": "<plugin>",
  "skills": "skills/",
  "version": "1.0.<Z>",
  "description": "<description> for GitHub Copilot.",
  "author": {"name": "rmompo", "email": "rmompo@gmail.com"}
}
```

2. For each skill included in this port, copy its SKILL.md:
```
ghcopilot/plugins/<plugin>/skills/<skill>/SKILL.md
```

3. Create `REPO_ROOT/ghcopilot/plugins/<plugin>/README.md` with skills table.

4. Update `REPO_ROOT/ghcopilot/MARKETPLACE.md` — add row:
```markdown
| [`<plugin>`](./plugins/<plugin>/README.md) | <status> | <skills list> |
```

5. Update `REPO_ROOT/ghcopilot/.github/plugin/marketplace.json` — add entry:
```json
{
  "name": "<plugin>",
  "description": "<description>",
  "version": "1.0.<Z>",
  "source": "./plugins/<plugin>"
}
```

### Antigravity / Codex ports

Apply equivalent scaffolding under `antigravity/<plugin>/` or `codex/<plugin>/` and update their respective MARKETPLACE.md and marketplace index files if they exist.

---

## Step 8 — Sync cache

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
✅ Plugin created: <plugin> v1.0.<Z>

Files created:
  claudecode/<plugin>/.claude-plugin/plugin.json
  claudecode/<plugin>/skills/<skill>/SKILL.md
  claudecode/<plugin>/README.md
  specs/<plugin>.md
  [ghcopilot/plugins/<plugin>/  — if ghcopilot port is beta/stable]

Catalogs updated:
  specs/catalog.json  →  ~/.p4/catalog.json (synced)
  .claude-plugin/marketplace.json
  claudecode/MARKETPLACE.md
  README.md  (plugins table)
  [ghcopilot/MARKETPLACE.md — if ghcopilot port is beta/stable]
  [ghcopilot/.github/plugin/marketplace.json — if ghcopilot port is beta/stable]

Cache synced: ~/.claude/plugins/cache/plugin4ai-claudecode/<plugin>/1.0.<Z>/

Next steps:
  1. Fill in skill logic in skills/<skill>/SKILL.md
  2. git add + commit + push
  3. claude plugins install <plugin>
```
