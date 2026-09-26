---
name: skill-doctor
description: Audits plugin skills for version mismatches, frontmatter issues, allowed-tools gaps, catalog inconsistencies, and structural defects. Emits a prioritized findings report and offers to fix auto-correctable defects. Also invoked explicitly as /p4-plugin:skill-doctor.
version: 25
argument-hint: "[plugin] [skill]"
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
---

# Skill Check

Audits one or more plugin skills for defects and inconsistencies. Produces a findings report with severity, fix type, and mitigation plan. Optionally auto-fixes eligible defects.

```
REPO_ROOT  = resolved via marketplace.json
CATALOG    = $REPO_ROOT/specs/catalog.json
CACHE_BASE = ~/.claude/plugins/cache/plugin4ai-claudecode
```

---

## Step 1 — Locate repo root and read catalog

```bash
find ~ -name "marketplace.json" -path "*plugin4ai*/.claude-plugin*" 2>/dev/null | head -1
# REPO_ROOT = two levels up
```

Read `CATALOG` into memory. Read the list of installed plugins from `CACHE_BASE`.

---

## Step 2 — Select scope

Use **AskUserQuestion** to ask the user what to audit:

- **All plugins — all skills** — full audit of everything installed
- **Specific plugin — all its skills** — show a sub-question to pick the plugin
- **Specific plugin:skill** — show plugin picker then skill picker

If "specific plugin" or "specific plugin:skill" is selected, present the available options from `CATALOG` as follow-up questions.

Build the **audit scope**: a list of `{plugin, skill}` pairs to check.

---

## Step 3 — Run checks

For each `{plugin, skill}` in scope, run the full battery of checks below. Collect every finding into a list.

Each finding has:
- `plugin`, `skill`
- `severity`: `CRITICAL` / `MAJOR` / `MINOR`
- `fix`: `[auto]` (can be corrected without human judgment) or `[manual]` (requires human review)
- `defect`: what is wrong
- `mitigation`: concrete action to fix it

### Check battery

#### C1 — SKILL.md version vs catalog  `CRITICAL · [auto]`
Read `$REPO_ROOT/claudecode/<plugin>/skills/<skill>/SKILL.md` frontmatter `version`.
Read `catalog["skills"][skill]["version"]`.
If they differ → defect.
```
Defect:    SKILL.md version: X ≠ catalog version: Y
Mitigate:  update SKILL.md frontmatter: version: X → Y
```

#### C2 — plugin.json version vs catalog  `CRITICAL · [auto]`
Read `$REPO_ROOT/claudecode/<plugin>/.claude-plugin/plugin.json` → `version`.
Read catalog plugin entry → `version`.
If they differ → defect.
```
Defect:    plugin.json version: X ≠ catalog version: Y
Mitigate:  update plugin.json: "version": "X" → "Y"
```

#### C3 — Cache out of sync with plugin.json  `CRITICAL · [auto]`
Check `$CACHE_BASE/<plugin>/` — the highest versioned directory must equal the plugin.json version.
If missing or lower → defect.
```
Defect:    cache at vX, plugin.json at vY — cache is stale
Mitigate:  re-sync cache (shutil.copytree)
```

#### C4 — Missing required frontmatter fields  `CRITICAL · [manual]`
SKILL.md frontmatter must contain: `name`, `description`, `version`, `allowed-tools`.
Flag each missing field individually.
```
Defect:    missing frontmatter field: <field>
Mitigate:  add <field> to SKILL.md frontmatter
```

#### C5 — allowed-tools gaps  `MAJOR · [manual]`
Scan the SKILL.md body for **explicit tool invocation signals** only. Do NOT match generic prose words — only patterns that unambiguously reference the Claude Code tool by name.

| Signal in body | Required tool | Rationale |
|---|---|---|
| `AskUserQuestion` | `AskUserQuestion` | Class name, no ambiguity |
| ` ```bash` | `Bash` | Fenced bash block = Bash tool invocation |
| `Read tool` or `the Read tool` or `Use Read` | `Read` | Explicit tool reference |
| `Write tool` or `the Write tool` or `Use Write` | `Write` | Explicit tool reference |
| `Edit tool` or `the Edit tool` or `Use Edit` | `Edit` | Explicit tool reference |

**Do NOT flag** on:
- `Read ` (space) alone — matches "Read this file", "Read requirements from catalog" (prose)
- `Write ` (space) alone — matches "Write the subject", "Write the entire response" (prose)
- `Edit ` (space) alone — matches "Edit `field`" in table cells (prose)
- `Bash` alone — matches "bash command", "Bash script" (prose)

For each tool signalled in the body but absent from `allowed-tools` → defect.
```
Defect:    body uses <tool> but it is not in allowed-tools
Mitigate:  add <tool> to allowed-tools list in SKILL.md frontmatter
```

#### C6 — Plugin has dependencies but no setup skill  `MAJOR · [manual]`
A plugin must have a skill named `setup` if **any** of the following is true:
- `catalog["plugins"][plugin]["dependencies"]` is non-empty (plugin-level dependency)
- Any skill in the plugin has `catalog["skills"][skill]["dependencies"]` non-empty (skill-level dependency)

Check reported once per plugin, not per skill.

The `setup` skill must verify **all dependency types**:
- `type: "tool"` — check via `which <name>` and compare version against constraint
- `type: "plugin"` — check via `ls ~/.claude/plugins/cache/plugin4ai-claudecode/<name>/` (installed if directory has at least one entry); install with `claude plugins install <name>`

The status table must include a `Type` column to distinguish tools from plugins.

```
Defect:    plugin has dependencies (plugin-level or skill-level) but no setup skill
Mitigate:  create a setup skill with /p4-plugin:skill-add
```

#### C7 — Description missing "Also invoked" suffix  `MINOR · [auto]`
SKILL.md description must end with `. Also invoked explicitly as /<plugin>:<skill>` (with optional args suffix).
```
Defect:    description missing standard invocation suffix
Mitigate:  append ". Also invoked explicitly as /<plugin>:<skill>." to description
```

#### C8 — Catalog changelog missing entry for current version  `MINOR · [auto]`
In `catalog["skills"][skill]["changelog"]`, the first entry `version` must equal `catalog["skills"][skill]["version"]`.
```
Defect:    no changelog entry for current skill version <V>
Mitigate:  insert {"version": V, "changes": "<describe>"} as first entry
```

#### C9 — skill-level dependencies in catalog not documented in SKILL.md  `MINOR · [manual]`
If `catalog["skills"][skill]["dependencies"]` is set, check that the SKILL.md body mentions the required tool(s) or plugin(s) explicitly (at least once).
```
Defect:    skill depends on <name> in catalog but body never references it
Mitigate:  add dependency verification step or note to SKILL.md body
```

---

## Step 4 — Emit findings report

If **no findings**: print `✅ No defects found in the audited scope.` and stop.

If findings exist, print:

```
══════════════════════════════════════════
  SKILL CHECK REPORT
  Scope: [all | <plugin> | <plugin>:<skill>]
  Audited: N plugins · M skills
══════════════════════════════════════════
```

Then print the findings table:

| # | plugin | skill | severity | fix | defect | mitigation plan |
|---|---|---|---|---|---|---|
| 1 | p4-core | skill-list | CRITICAL | [auto] | SKILL.md version 7 ≠ catalog version 8 | update SKILL.md frontmatter version: 7 → 8 |
| 2 | p4-ccvv | generate | MAJOR | [manual] | body uses AskUserQuestion but not in allowed-tools | add AskUserQuestion to allowed-tools |
| 3 | p4-converter | any-to-md | MINOR | [auto] | description missing invocation suffix | append ". Also invoked explicitly as /p4-converter:any-to-md." |

Sort by: severity (`CRITICAL` first, then `MAJOR`, then `MINOR`), then plugin ASC, then skill ASC.

Print summary footer:
```
Findings: N total · C critical · M major · m minor
Auto-fixable: A · Manual: B
```

---

## Step 5 — Offer fixes

Use **AskUserQuestion** to ask the user what to fix:

- **Fix all auto-fixable** — apply every `[auto]` fix automatically
- **Fix specific findings** — user selects by number (e.g. `1, 3, 5`)
- **Nothing — report only** — exit without changes

If "nothing" → print `Report saved. No changes applied.` and stop.

---

## Step 6 — Apply auto fixes

For each selected `[auto]` finding, apply the mitigation programmatically:

**C1 — SKILL.md version:**
```bash
# Read SKILL.md, replace "version: X" with "version: Y" in frontmatter
sed -i "s/^version: .*/version: Y/" $REPO_ROOT/claudecode/<plugin>/skills/<skill>/SKILL.md
```

**C2 — plugin.json version:**
```python
pj = json.load(open(pj_path))
pj["version"] = catalog_version
open(pj_path, 'w').write(json.dumps(pj, indent=2, ensure_ascii=False) + '\n')
```

**C3 — Cache sync:**
```python
# Remove old cache, copytree from plugin_dir to cache/new_version
```

**C7 — Description suffix:**
```bash
# Append suffix to description line in SKILL.md frontmatter
```

**C8 — Changelog entry:**
```python
skill_entry["changelog"].insert(0, {"version": new_Z, "changes": "version bump"})
open(catalog_path, 'w').write(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')
```

For `[manual]` findings that were selected → print:
```
⚠️  Finding #N is [manual] — cannot be auto-fixed.
    Defect:   <defect>
    Action:   <mitigation plan>
```

After all fixes applied, re-sync cache for any plugin that was modified.

---

## Step 7 — Summary

```
══════════════════════════════════════════
  FIX SUMMARY
══════════════════════════════════════════
  Fixed (auto):   N findings
  Skipped (manual): M findings
  Unchanged:      K findings

  Modified files:
    claudecode/<plugin>/skills/<skill>/SKILL.md
    claudecode/<plugin>/.claude-plugin/plugin.json
    specs/catalog.json

  Cache re-synced: <plugin> v<version>
══════════════════════════════════════════

Next steps:
  1. Review manual findings above
  2. git add + commit + push
  3. claude plugins update <plugin>
```
