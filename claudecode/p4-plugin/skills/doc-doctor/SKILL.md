---
name: doc-doctor
description: Audits documentation completeness and language for each plugin: verifies spec files, MARKETPLACE.md listing, README.md skills tables, and English-only content against catalog ground truth. Reports findings and offers to generate or update missing content automatically. Also invoked explicitly as /p4-plugin:doc-doctor.
version: 26
argument-hint: "[plugin]"
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
---

# Doc Doctor

Audits and updates plugin documentation. Checks `specs/<plugin>.md`, `claudecode/MARKETPLACE.md`, `claudecode/<plugin>/README.md`, and language compliance against `specs/catalog.json`. All content must be written in English.

```
REPO_ROOT      = resolved via marketplace.json
CATALOG        = $REPO_ROOT/specs/catalog.json
MARKETPLACE_MD = $REPO_ROOT/claudecode/MARKETPLACE.md
```

---

## Step 1 — Locate repo root and read catalog

```bash
find ~ -name "marketplace.json" -path "*plugin4ai*/.claude-plugin*" 2>/dev/null | head -1
# REPO_ROOT = two levels up
```

Read `CATALOG` into memory.

---

## Step 2 — Select scope

If the skill was invoked with a `$ARGUMENTS` value, use it as the plugin filter and skip the question.

Otherwise, use **AskUserQuestion** to ask:

- **All plugins** — audit every plugin registered in catalog
- **Specific plugin** — pick from the plugin list in catalog

Build the **audit scope**: a list of plugin names to check.

---

## Step 3 — Run checks

For each plugin in scope, run all checks below. Collect every finding into a list.

Each finding has:
- `plugin`
- `check`: check ID (D1–D8)
- `severity`: `CRITICAL` / `MAJOR` / `MINOR`
- `fix`: `[auto]` or `[manual]`
- `defect`: what is wrong
- `detail`: specific missing element or value
- `mitigation`: concrete action to fix it

### Check battery

#### D1 — Spec file missing  `CRITICAL · [auto]`

Check whether `$REPO_ROOT/specs/<plugin>.md` exists.

```bash
test -f "$REPO_ROOT/specs/<plugin>.md"
```

If missing → defect. Auto-fix generates the full spec from catalog data.

```
Defect:    specs/<plugin>.md does not exist
Mitigate:  generate spec file from catalog entry
```

#### D2 — Spec missing required sections  `MAJOR · [auto]`

Read `specs/<plugin>.md`. Check for the presence of these sections (case-insensitive heading match):

| Required section | Pattern to match |
|-----------------|-----------------|
| Overview | `## Overview` |
| Port Status | `## Port Status` |
| Changelog | `## Changelog` |

For each missing section → one finding.

```
Defect:    specs/<plugin>.md is missing required section: <section>
Mitigate:  add <section> section with template content
```

#### D3 — Spec missing section for a catalog skill  `MAJOR · [auto]`

For each skill listed in `catalog["skills"]` for this plugin, check whether the spec references it.

Accept either format:
- Explicit section: `## Skill: \`<skill>\`` or `## Skill: <skill>`
- Skills table row: a Markdown table row or list item containing the skill name

```bash
grep -i "<skill>" "$REPO_ROOT/specs/<plugin>.md"
```

If the skill name does not appear anywhere in the spec → defect.

```
Defect:    specs/<plugin>.md has no documentation for skill: <skill>
Mitigate:  add ## Skill: `<skill>` section with Purpose, Invocation, Non-Goals
```

#### D4 — Spec version header does not match catalog  `MINOR · [auto]`

Look for the version string in the spec status line (e.g., `**Version:** \`1.1.9\``).

Compare against `catalog["plugins"][plugin]["version"]`.

If they differ → defect.

```
Defect:    spec version header shows <A>, catalog is at <B>
Mitigate:  update version string in spec status line
```

#### D5 — Plugin not listed in MARKETPLACE.md  `MAJOR · [auto]`

Read `$REPO_ROOT/claudecode/MARKETPLACE.md`.

Check whether a row exists for this plugin in the "Available plugins" table (match on plugin name in the first column).

If not found → defect. Auto-fix adds a new row.

```
Defect:    claudecode/MARKETPLACE.md has no row for plugin <plugin>
Mitigate:  add row: | [`<plugin>`](./<plugin>/README.md) | <status> | `<skills>` | — |
```

#### D6 — MARKETPLACE.md row has incomplete skills list  `MINOR · [auto]`

Parse the MARKETPLACE.md row for this plugin. Extract the skills listed in the "Skills" column.

Compare against all skills in `catalog["skills"]` for this plugin.

If any skill is missing from the row → defect.

```
Defect:    MARKETPLACE.md row for <plugin> is missing skill(s): <skill1>, <skill2>
Mitigate:  update skills column to: `<skill1>`, `<skill2>`, ...
```

#### D7 — README.md missing or skills table incomplete  `MAJOR · [auto]`

Check `$REPO_ROOT/claudecode/<plugin>/README.md`:

1. If file does not exist → defect (generate full README).
2. If file exists, check that every skill in `catalog["skills"]` appears in the README.
   - If any skill is absent → defect (add missing rows).

```
Defect:    claudecode/<plugin>/README.md does not exist
Mitigate:  generate README.md from catalog data

Defect:    claudecode/<plugin>/README.md is missing entry for skill: <skill>
Mitigate:  add row to skills table: | `<skill>` | `/<plugin>:<skill>` | <description> |
```

**Note:** D7 is always `[auto]` — the README content is derived deterministically from catalog data and SKILL.md descriptions.

#### D9 — Plugin dependencies not documented in README.md  `MAJOR · [auto]`

If the plugin has any `type: "plugin"` entries in its `dependencies` array, the `README.md` must document them.

Check whether `claudecode/<plugin>/README.md` contains a `## Dependencies` section listing the required plugins.

```
Defect:    plugin has type:"plugin" dependencies but README.md has no ## Dependencies section
Mitigate:  add ## Dependencies section to README.md listing the required plugins with install instructions
```

Auto-fix generates a `## Dependencies` section inserted before `## Installation`:

```markdown
## Dependencies

This plugin requires the following plugins to be installed:

| Plugin | Install |
|--------|---------|
| `<plugin>` | `claude plugins install <plugin>` |
```

---

#### D8 — Documentation not in English  `MAJOR · [auto]`

All plugin documentation must be written in English. Check the following files:
- `specs/<plugin>.md`
- `claudecode/<plugin>/README.md`

For each file, scan:
1. All `##` and `###` headings for non-ASCII characters (accented letters indicate non-English).
2. The Overview / description paragraphs for common non-English stopwords in headings (e.g. Spanish: `el`, `la`, `los`, `de`, `del`, `en`, `con`, `para`, `que`, `es`, `una`).
3. Any section that is visually identifiable as non-English prose.

```bash
grep -P '[^\x00-\x7F]' "$REPO_ROOT/specs/<plugin>.md"
grep -P '[^\x00-\x7F]' "$REPO_ROOT/claudecode/<plugin>/README.md"
```

```
Defect:    specs/<plugin>.md contains non-English content in section: <section>
Mitigate:  translate affected section to English

Defect:    claudecode/<plugin>/README.md contains non-English content
Mitigate:  rewrite affected content in English
```

---

## Step 4 — Emit findings report

If **no findings**: print `✅ No documentation gaps found in the audited scope.` and stop.

If findings exist, print:

```
══════════════════════════════════════════
  DOC DOCTOR REPORT
  Scope: [all | <plugin>]
  Audited: N plugins · D9 checks each
══════════════════════════════════════════
```

Then print the findings table:

| # | plugin | check | severity | fix | defect | detail | mitigation plan |
|---|--------|-------|----------|-----|--------|--------|-----------------|
| 1 | p4-buddy | D1 | CRITICAL | [auto] | spec file missing | specs/p4-buddy.md | generate from catalog |
| 2 | p4-plugin | D3 | MAJOR | [auto] | skill not documented | skill-doctor | add ## Skill: `skill-doctor` section |
| 3 | p4-core | D7 | MAJOR | [auto] | README.md missing skill | skill-list | add row to skills table |
| 4 | p4-plugin | D8 | MAJOR | [auto] | non-English content | specs/p4-plugin.md §Overview | translate to English |

Sort by: severity (`CRITICAL` first, then `MAJOR`, then `MINOR`), then plugin ASC, then check ASC.

Print summary footer:
```
Findings: N total · C critical · M major · m minor
Auto-fixable: A · Manual: B
```

---

## Step 5 — Offer fixes

Use **AskUserQuestion** to ask what to do:

- **Fix all auto-fixable** — apply every `[auto]` fix automatically
- **Fix specific findings** — user selects by number (e.g. `1, 3, 5`)
- **Nothing — report only** — exit without changes

If "nothing" → print `Report saved. No changes applied.` and stop.

---

## Step 6 — Apply auto fixes

Apply each selected `[auto]` fix as follows.

### D1 — Generate full spec file

Generate `specs/<plugin>.md` using the canonical template, populating it with data from `catalog`. All content must be in English:

```markdown
# Plugin Spec: <plugin>

> **Status:** `<status>` | **Version:** `<version>` | **Ports:** Claude Code only

## Overview

<plugin description from catalog — in English>

---

## Skill: `<skill>`

### Purpose
<skill purpose inferred from SKILL.md description — in English>

### Invocation
/<plugin>:<skill> [args]

### Non-Goals
- <to be defined>

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code | `claudecode/<plugin>/` | ✅ Beta |

## Changelog

| Version | Changes |
|---------|---------|
<entries from catalog plugin changelog — in English>
```

### D2 — Add missing top-level section

Use the Edit tool to insert the missing section at the correct position:

- **Overview**: insert after the status line
- **Port Status**: insert before Changelog
- **Changelog**: append at end, generated from `catalog["plugins"][plugin]["changelog"]`

### D3 — Add missing skill section

Use the Edit tool to insert before `## Port Status` (or append if absent):

```markdown
---

## Skill: `<skill>`

### Purpose
<description from catalog skill entry — in English>

### Invocation
/<plugin>:<skill>

### Non-Goals
- <to be defined>
```

### D4 — Update spec version header

Use the Edit tool to replace the version string in the status line:

```
**Version:** `<old>` → **Version:** `<new>`
```

### D5 — Add plugin row to MARKETPLACE.md

Use the Edit tool to insert a new row in the "Available plugins" table before the closing blank line:

```
| [`<plugin>`](./<plugin>/README.md) | <status> | `<skill1>`, `<skill2>`, ... | — |
```

### D6 — Update MARKETPLACE.md skills column

Use the Edit tool to replace the row's skills column with the complete list from catalog:

```
`skill1`, `skill2`, `skill3`, ...
```

### D7 — Generate or update README.md

**If README.md does not exist**, use the Write tool to create it:

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

**If README.md exists but is missing skills**, use the Edit tool to insert the missing row(s) into the skills table. Read the skill description from the SKILL.md frontmatter (first sentence before ". Also invoked").

All README content must be in English.

### D8 — Fix non-English content

Use the Edit tool to translate or rewrite the identified non-English section(s) to English. Preserve all technical terms, code blocks, and Markdown structure — only the prose content is translated.

### D9 — Add plugin dependencies section to README.md

Use the Edit tool to insert a `## Dependencies` section before `## Installation` in `claudecode/<plugin>/README.md`:

```markdown
## Dependencies

This plugin requires the following plugins to be installed:

| Plugin | Install |
|--------|---------|
| `<plugin>` | `claude plugins install <plugin>` |
```

List one row per `type: "plugin"` entry in the plugin's `dependencies` array.

---

## Step 7 — Summary

```
══════════════════════════════════════════
  DOC DOCTOR SUMMARY
══════════════════════════════════════════
  Fixed (auto):     N findings
  Skipped (manual): M findings
  Unchanged:        K findings

  Modified files:
    specs/<plugin>.md
    claudecode/<plugin>/README.md
    claudecode/MARKETPLACE.md

══════════════════════════════════════════

Next steps:
  1. Review generated/updated content
  2. git add + commit + push
```
