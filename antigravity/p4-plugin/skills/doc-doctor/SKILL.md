---
name: doc-doctor
description: Runs documentation quality checks on a plugin — spec file, README, catalog alignment, skills documentation, and English language. Also invoked explicitly as /p4-plugin:doc-doctor with the plugin name.
---

# Doc Doctor (Antigravity CLI)

Audits the documentation of a plugin and reports quality issues.

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
```

---

## Step 2 — Run checks

### D1 — Spec file exists

Check that `specs/<plugin>.md` exists.

**Severity: ERROR** if missing.

---

### D2 — Spec has required sections

The spec file `specs/<plugin>.md` must contain:
- A top-level heading with the plugin name
- A `## Skills` section
- A `## Ports` section
- A `## Changelog` section

**Severity: WARNING** per missing section.

---

### D3 — All skills documented in spec

Every skill listed in `plugin_entry["skills"]` in catalog.json should appear in the `## Skills` section of `specs/<plugin>.md`.

**Severity: WARNING** per missing skill.

---

### D4 — Version in spec matches catalog

The latest version mentioned in `specs/<plugin>.md` (e.g., under `## Changelog`) should match `plugin_entry["version"]`.

**Severity: WARNING** if mismatched.

---

### D5 — README exists

Check that `antigravity/<plugin>/README.md` exists.

**Severity: ERROR** if missing.

---

### D6 — README has required sections

`antigravity/<plugin>/README.md` must contain:
- A top-level heading with the plugin name
- A `## Skills` section
- An `## Installation` section (with `agy plugin install` command)

**Severity: WARNING** per missing section.

---

### D7 — README skills match catalog

Every skill in `plugin_entry["skills"]` should be listed in the README skills table.

**Severity: WARNING** per skill not listed.

---

### D8 — Descriptions in English

The `description` field of the plugin and all skills in catalog.json should be written in English.

**Severity: WARNING** if non-English description detected.

---

### D9 — Plugin dependencies documented

If `plugin_entry["dependencies"]` is non-empty, the README should mention those dependencies.

**Severity: INFO** if dependencies are unlisted in README.

---

## Step 3 — Output report

```
══════════════════════════════════════════════════════════════════════
  DOC DOCTOR: <plugin>  (Antigravity CLI)
══════════════════════════════════════════════════════════════════════

  ✅ D1 Spec file: specs/<plugin>.md exists
  ✅ D2 Spec sections: all required sections present
  ✅ D3 Skills in spec: all N skills documented
  ✅ D4 Spec version: matches catalog (v<version>)
  ✅ D5 README exists: antigravity/<plugin>/README.md
  ⚠️  D6 README sections: missing ## Installation
  ✅ D7 README skills: all skills listed
  ✅ D8 Descriptions in English
  ℹ️  D9 Dependencies: 'python3' not mentioned in README

──────────────────────────────────────────────────────────────────────
Summary
  Errors:         N  (must fix)
  Warnings:       N  (should fix)
  Info:           N  (optional)
══════════════════════════════════════════════════════════════════════
```

---

## Step 4 — Offer to fix

For each issue found, offer to fix it automatically where safe (e.g., adding a missing section, updating the version). Always ask before applying any fix.
