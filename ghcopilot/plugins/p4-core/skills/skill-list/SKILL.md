---
name: skill-list
description: Lists all p4-* plugin skills installed in the current CLI, in a table with columns plugin|skill|v|ready|description. Also invoked explicitly as /p4-core:skill-list.
version: 22
allowed-tools: [Bash, Read]
---

## Step 0 — Detect CLI and cache base

```bash
# GitHub Copilot
CACHE_BASE=~/.ghcopilot/plugins/cache/plugin4ai-ghcopilot
CATALOG=~/.p4/catalog.json
[ ! -f "$CATALOG" ] && CATALOG=~/.ghcopilot/plugins/marketplaces/plugin4ai-ghcopilot/specs/catalog.json
```

---

# Skill List

Lists all p4-* plugin skills installed in the current CLI, in a Markdown table with columns `plugin | skill | v | ready | description`.

Only plugins compatible with the current CLI are included.

---

## Step 1 — Enumerate p4-* plugins

```bash
ls "$CACHE_BASE" | grep "^p4-"
# For each plugin, take the highest installed version
```

---

## Step 2 — Read skills for each plugin

For each plugin found:

```bash
# Read plugin.json to get the active version
cat "$CACHE_BASE/<plugin>/<version>/plugin.json"

# Read each SKILL.md to get name, version and description
cat "$CACHE_BASE/<plugin>/<version>/skills/<skill>/SKILL.md"
```

Extract from the YAML frontmatter of each SKILL.md:
- `name` → skill name (primary identifier)
- `description` → **description** column (first sentence before ". Also invoked")

**Skill version is always read from `catalog.json`**, not from SKILL.md frontmatter. The catalog is the source of truth.

```python
skill_version = catalog["plugins"][plugin]["skills"][skill_name]["version"]
```

---

## Step 3 — Determine enabled status (visual indicator)

Enabled status is shown as an emoji prefix on the `plugin` and `skill` cells — not as a separate column:

- **Plugin enabled** → its directory exists in cache with at least one installed version → 🟢 prefix on the `plugin` cell.
- **Plugin disabled** → not in cache → 🔴 prefix on the `plugin` cell.
- **Skill enabled** → SKILL.md exists in the active version of the plugin in cache → 🟢 prefix on the `skill` cell.
- **Skill disabled** → SKILL.md does not exist → 🔴 prefix on the `skill` cell.

No `enabled` column in the table.

---

## Step 3b — Determine ready status

`ready` indicates whether the skill is **usable as-is** — either it has no external dependencies, or all of its dependencies are present.

For each skill, resolve its dependency list with the following priority:

1. **Skill-level `dependencies`** in `catalog.json` → use that list
2. **Plugin-level `dependencies`** in `catalog.json` (if skill has none) → use plugin-level list
3. **No dependencies** → skill is unconditionally ready

**Unconditional exception:** the `setup` skill always shows an empty `ready` column.

For each dependency in the resolved list, check by type:

| Type | How to check |
|------|-------------|
| `tool` | `which <name> 2>/dev/null` — present if exit code 0 |
| `plugin` | `ls $CACHE_BASE/<name>/ 2>/dev/null` — installed if directory has at least one entry |

- **No dependencies** → `ready` = `✅`
- **All dependencies satisfied** → `ready` = `✅`
- **Any dependency missing** → `ready` = `❌`

---

## Step 4 — Print table

Output format: **Unicode box-drawing table**, wrapped in a ` ```text ` code block to preserve monospace alignment.

---

### 4.1 — Column widths

- Columns `plugin`, `skill`, `v`, `ready`: dynamic width = `max(header_width, longest_content) + 2` (1 space padding each side).
- Column `description`: **fixed width of 62** (60 chars of content + 2 padding).
- **Emojis** 🟢 🔴 ✅ ❌ occupy **2 terminal columns**. Compensate by subtracting 1 per emoji when calculating space padding.

---

### 4.2 — Separator types

Two types — never just one:

| Type | When | Structure |
|------|------|-----------|
| **Full** | Between plugins / after header / top and bottom border | `├─────┼─────┼─────┼─────┼─────┤` (crosses all columns) |
| **Partial** | Between skills of the same plugin | `│ {plugin_cell} ├─────┼─────┼─────┼─────┤` (plugin column continues with `│`, others with `├─┼─┤`) |

---

### 4.3 — Alignment

- **Headers**: **centered** within each column.
- **Data**: **left-aligned** in all columns.

---

### 4.4 — `plugin` column — always 2 physical content lines

The `plugin` column has **exactly 2 content lines** per plugin group, counting all physical lines:

| Physical line index within group | Content in `plugin` column |
|----------------------------------|---------------------------|
| 0 | `🟢 {plugin_name}` or `🔴 {plugin_name}` |
| 1 | `(v{plugin_version})` e.g. `(v1.2.18)` |
| ≥ 2 | empty |

---

### 4.5 — Per-column rules

- **`plugin`**: see §4.4. Never repeats within the same group.
- **`skill`**: `🟢 {skill_name}` or `🔴 {skill_name}`. Only on the first physical line of the skill.
- **`v`**: integer skill version. Only on the first physical line of the skill.
- **`ready`**: `✅` / `❌` per dependencies; **empty** for the `setup` skill. Only on the first physical line.
- **`description`**: full first sentence up to ". Also invoked", no truncation. Wrap at 60 chars if longer; other columns stay empty on wrap lines.

Column order: `plugin │ skill │ v │ ready │ description`

---

### 4.6 — Footer

Print immediately after the table (outside the code block):

```
**N plugins · M skills · M enabled**
```

Sort by `plugin` ASC, then `skill` ASC within each group.
