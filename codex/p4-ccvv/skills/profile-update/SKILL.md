---
name: profile-update
description: Updates an existing profile.json with new or corrected data. Creates an automatic backup before any modification.
---

# Profile Update

Updates fields in an existing `profile.json`. Always creates a timestamped backup before writing.

```
STORAGE_ROOT = ~/.p4/p4-ccvv
```

---

## Step 1 — Select user

Read `~/.p4/p4-ccvv/profiles.json`. Ask the user (via plain text) to select the profile to update.

Verify `profiles/[user]/data/profile.json` exists. If not, suggest running `/p4-ccvv:profile-gather` first.

---

## Step 2 — Select update mode

Ask the user (via plain text) to choose:
- **Document-based**: user provides a new/updated CV file in `input/` — re-extract specific sections
- **Interactive**: guided field-by-field update

---

## Step 3 — Backup

Before any modification:
```bash
cp profile.json profile.json.backup-$(date +%Y%m%dT%H%M%S)
```

---

## Step 4 — Apply updates

### Document-based mode
Ask which section to update (experience, education, skills, knowledge, projects, languages, interests). Re-extract only that section from the selected file and merge into profile.json.

### Interactive mode
Ask what the user wants to update. Supported operations:

| Operation | What it does |
|-----------|-------------|
| Add experience | Append new entry to `experience[]` |
| Add education | Append new entry to `education[]` |
| Add/update skills | Replace or extend `skills[]` |
| Add/update knowledge | Add category or extend values |
| Add project | Append new entry to `projects[]` |
| Update contact | Edit `info.contact` fields (email, phone, location) |
| Update languages | Edit `languages[]` entries |
| Update interests | Replace `interests[]` |
| Add/update social networks | Add or update professional network and repository links in `contact.others` |

**Social networks operation detail:**

Present the current `contact.others` entries (if any) and allow the user to add, update or remove links. Supported platforms and their type keys: `linkedin`, `github`, `gitlab`, `stackoverflow`, `portfolio`, `medium`, `devto`, `hashnode`, `credly`, `npm`, `pypi`.

For each entry: collect `type` and `value` (valid URL). If the type already exists, update its value — do not duplicate. Accept only valid URLs. Never store empty values.

Collect field values via plain text prompts. Never modify fields not explicitly requested.

---

## Step 5 — Update metadata

Set `metadata.updated` to current ISO 8601 timestamp. Bump `metadata.version` by +0.1.

---

## Step 6 — Validate and save

Validate against `profile.schema.json`. If valid, save. If not, report errors and ask to correct before saving.

Print summary:
```
✅ Profile updated: ~/.p4/p4-ccvv/profiles/[user]/data/profile.json
   Version: X.X | Backup: profile.json.backup-[timestamp]
```
