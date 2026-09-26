---
name: regen
description: Regenerates existing CV drafts using updated profile data, preserving original job parameters and keywords. Also invoked explicitly as /p4-ccvv:regen.
version: 5
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# Regen CV

Regenerates a previously generated CV draft with the current `profile.json` data. Preserves all original parameters (position, offer, keywords, company). Only the content and `updated` timestamp change.

```
STORAGE_ROOT = ~/.p4/p4-ccvv
GUIDELINES   = <plugin-cache>/resources/CV-GENERATION-GUIDELINES.md
```

---

## Step 1 — Select user

Read `profiles.json`. Use **AskUserQuestion** to select the profile.

Verify both `profile.json` and `cvs.json` exist.

---

## Step 2 — Select CV to regenerate

Read `cvs.json`. Display existing CVs using **AskUserQuestion**:

| # | Position | Company | Generated | Exports |
|---|----------|---------|-----------|---------|
| 1 | Developer Full Stack | — | 2026-02-04 | 3 |
| 2 | Programador Backend | Acme | 2026-03-01 | 1 |

---

## Step 3 — Read original parameters

From the selected metadata entry, extract:
- `position`, `company`, `parameters`, `keywords`, `offer_analyzed`, `slug`, `folder`

Read the original META file to preserve YAML front-matter fields: `metadata_id`, `slug`, `generado`, `offer_analyzed`, `keywords`.

---

## Step 4 — Regenerate draft

Read updated `profile.json`. Apply all GUIDELINES rules identically to `/p4-ccvv:generate` Step 5, but:

- Keep `metadata_id`, `slug`, `generado`, `offer_analyzed`, `keywords` from original
- Set `actualizado` to current ISO 8601 timestamp
- Adapt content to job parameters from original entry

Overwrite the existing META file. Do NOT create a new metadata ID.

If a LETTER file exists alongside the CV, regenerate it too.

---

## Step 5 — Update cvs.json

Set `metadata[n].updated` to current timestamp.

---

## Step 6 — Confirm

```
✅ CV regenerated: CV-[id_padded]-META-[slug]-CV.md
   Profile version used: X.X | Updated: [timestamp]
```
