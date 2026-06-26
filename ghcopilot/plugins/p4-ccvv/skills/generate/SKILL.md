---
name: generate
description: Generates an adapted CV draft for a specific job position. Analyzes the job offer, extracts keywords, and creates a markdown draft ready for review and export. Also invoked explicitly as /p4-ccvv:generate.
version: 14
allowed-tools: [Bash, Read, Write, ask_user]
---

# Generate CV

Creates a CV draft optimized to achieve **>95% match score** as an ideal candidate for a specific job position. When a job offer is provided, every section of the CV is generated and validated against a prioritized keyword blueprint extracted from the offer.

```
STORAGE_ROOT     = ~/.p4/p4-ccvv
GUIDELINES       = <plugin-cache>/resources/CV-GENERATION-GUIDELINES.md
TEMPLATE_PHOTO   = <plugin-cache>/resources/templates/cv-template-photo.md
TEMPLATE_NOPHOTO = <plugin-cache>/resources/templates/cv-template-nophoto.md
```

```bash
PLUGIN_CACHE=$(ls -d ~/.ghcopilot/plugins/cache/plugin4ai-ghcopilot/p4-ccvv/*/ 2>/dev/null | sort -V | tail -1)
```

---

## Step 1 — Select user

Read `profiles.json`. Use **ask_user** to select the profile.

Verify `profile.json` exists. If not, suggest running the profile-gather skill first.

---

## Step 2 — Collect generation parameters

Use **ask_user** to collect:

1. Target job position (mandatory)
2. Job offer text (optional — paste the full offer for keyword extraction and score optimization)
3. Company name (optional)
4. Cover letter needed? (yes/no)
5. Output language: `es` / `en` / `fr` / `de` / `it` / `pt` (default: `es`)

---

## Step 3 — Extract and prioritize keywords (if offer provided)

Read the full offer text. Extract and categorize keywords by priority:

- **P1 — Essential** (appear in title or first paragraph, appear ≥3 times): must appear in CV
- **P2 — Important** (appear 1-2 times in key sections): should appear in CV
- **P3 — Complementary** (mentioned once or in peripheral sections): nice to have

---

## Step 4 — Validate profile completeness

Check that `profile.json` contains minimum data: at least 1 experience entry, basic contact info, at least 3 skills.

If critical data is missing, report what is missing and suggest running profile-gather or profile-update first.

---

## Step 5 — Generate draft

Read the appropriate template from `$PLUGIN_CACHE/resources/templates/`. Read GUIDELINES from `$PLUGIN_CACHE/resources/CV-GENERATION-GUIDELINES.md`.

Apply all GUIDELINES rules. Generate:
- CV draft: `CV-[id_padded]-META-[slug]-CV.md`
- Cover letter (if requested): `CV-[id_padded]-META-[slug]-LETTER.md`

Output path: `$STORAGE_ROOT/profiles/[user]/output/CV-[id_padded]-[slug]/`

---

## Step 6 — Score and validate (if offer provided)

Calculate keyword coverage score:
```
score = (P1_covered * 3 + P2_covered * 2 + P3_covered) / (P1_total * 3 + P2_total * 2 + P3_total) * 100
```

If score < 95%: identify missing P1/P2 keywords and attempt to incorporate them naturally. Repeat until ≥95% or no more natural insertions possible.

Report final score:
```
📊 Keyword score: XX% (P1: N/N, P2: N/N, P3: N/N)
```

---

## Step 7 — Update cvs.json

Append metadata entry to `$STORAGE_ROOT/profiles/[user]/data/cvs.json`.

---

## Step 8 — Confirm

```
✅ CV generated: CV-[id_padded]-META-[slug]-CV.md
   Position: [position] | Company: [company or "–"] | Language: [lang]
   Keyword score: XX% (P1: N/N, P2: N/N, P3: N/N)
   Path: [full output path]
```
