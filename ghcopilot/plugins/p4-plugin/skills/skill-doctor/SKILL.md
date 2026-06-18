---
name: skill-doctor
description: Runs health checks on all skills of a plugin — frontmatter validity, catalog alignment, version consistency, dependencies. Also invoked explicitly as /p4-plugin:skill-doctor with the plugin name.
---

# Skill Doctor (GitHub Copilot)

Audits all skills of a plugin and reports issues with severity ratings.

---

## Step 0 — Locate repo root

```bash
git rev-parse --show-toplevel 2>/dev/null
```

---

## Step 1 — Load state

```python
import json, os
catalog = json.load(open(f"{REPO_ROOT}/specs/catalog.json"))
plugin_entry = next(p for p in catalog["plugins"] if p["name"] == plugin_name)
skills_dir = f"{REPO_ROOT}/ghcopilot/plugins/{plugin_name}/skills"
```

---

## Step 2 — Run checks per skill

For each skill directory found under `ghcopilot/plugins/<plugin>/skills/`:

### C1 — Frontmatter: required fields present

Every `SKILL.md` must have **both** fields in the YAML frontmatter:
- `name`
- `description`

No other fields are required for GitHub Copilot. Fields like `version`, `allowed-tools`, `argument-hint` are NOT expected and should not be flagged as missing.

**Severity: ERROR** if `name` or `description` is missing.

---

### C2 — Catalog registration

Every skill directory must have a corresponding entry in `plugin_entry["skills"]`.

**Severity: WARNING** if a skill directory exists but is not in the catalog.  
**Severity: WARNING** if the catalog lists a skill that has no directory.

---

### C3 — Skill catalog version

Check that the skill `version` in catalog.json follows the `X.Y.Z` format.

**Severity: WARNING** if the version is malformed.

---

### C4 — Description quality

The `description` field in SKILL.md frontmatter should:
- Be at least 20 characters long
- Not end with a period

**Severity: WARNING** if either check fails.

---

### C5 — Changelog entry

When a skill version in catalog.json changes, there should be a corresponding entry in `plugin_entry["changelog"]`.

**Severity: INFO** if the latest skill version has no matching changelog entry.

---

### C6 — Dependencies documented

If the skill body references external tools (bash commands like `jq`, `python3`, `git`, etc.), those tools should be listed in `plugin_entry["dependencies"]` in catalog.json, or there should be a `setup` skill in the plugin.

**Severity: WARNING** if undocumented tools are referenced.

---

### C7 — SKILL.md file exists

Every catalog skill entry must have a corresponding `SKILL.md` file.

**Severity: ERROR** if missing.

---

### C8 — Plugin version alignment

The version in `ghcopilot/plugins/<plugin>/plugin.json` should match `plugin_entry["version"]` in catalog.json.

**Severity: WARNING** if mismatched.

---

## Step 3 — Output report

```
══════════════════════════════════════════════════════════════════════
  SKILL DOCTOR: <plugin>  (GitHub Copilot)
══════════════════════════════════════════════════════════════════════

Skill: <skill>
  ✅ C1 Frontmatter: name + description present
  ✅ C2 Catalog registration: found
  ✅ C3 Catalog version: valid format
  ✅ C4 Description quality: OK
  ✅ C5 Changelog entry: found
  ⚠️  C6 Dependencies: references 'python3' — not in plugin dependencies
  ✅ C7 SKILL.md file exists
  ✅ C8 Plugin version aligned

[...repeat per skill...]

──────────────────────────────────────────────────────────────────────
Summary
  Skills checked: N
  Errors:         N  (must fix)
  Warnings:       N  (should fix)
  Info:           N  (optional)
══════════════════════════════════════════════════════════════════════
```

Severity guide:
- ❌ ERROR — skill will not work correctly; must fix
- ⚠️  WARNING — degrades quality or maintainability; should fix
- ℹ️  INFO — optional improvement

---

## Step 4 — Offer to fix

For each issue found, offer to fix it automatically if a safe automated fix is available (e.g., adding a missing changelog entry, updating plugin.json version). Always ask before applying any fix.
