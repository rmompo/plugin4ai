---
name: profile-gather
description: Extracts structured profile data from a source CV file (PDF/DOCX) and saves it to the user's profile.json.
---

# Profile Gather

Reads a CV source file and extracts all data into a structured `profile.json` following the profile schema.

```
STORAGE_ROOT = ~/.p4/p4-ccvv
SCHEMA       = <plugin-cache>/resources/schemas/profile.schema.json
```

---

## Step 1 — Locate storage and plugin resources

```bash
STORAGE_ROOT=~/.p4/p4-ccvv
PLUGIN_CACHE=$(ls -d ~/.gemini/config/plugins/cache/plugin4ai-antigravity/p4-ccvv/*/ 2>/dev/null | sort -V | tail -1)
PROFILES_JSON=$STORAGE_ROOT/profiles.json
```

Create `$STORAGE_ROOT/profiles/` if it doesn't exist.

---

## Step 2 — Select or create user

Read `$PROFILES_JSON` (create empty registry if absent).

Ask the user (via plain text) to select an existing profile or enter a new one.

**If new profile**: collect profile ID (alphanumeric + underscore, 3-20 chars, lowercase), full name, email. Create:
```
$STORAGE_ROOT/profiles/[id]/input/
$STORAGE_ROOT/profiles/[id]/data/
$STORAGE_ROOT/profiles/[id]/output/
```
Add entry to `profiles.json`.

---

## Step 3 — Request source files

### 3a — CV file

Ask the user (via plain text) for the **CV file path** (required): absolute or `~/`-prefixed path to their CV (`.pdf` or `.docx`).

Validate:
- Expand `~` to the actual home directory before any file operation.
- File must exist and have extension `.pdf` or `.docx`; if not, report the error and ask again.

Copy to the profile input folder and store the filename in `SOURCE_FILE`:
```bash
cp "$CV_PATH" "$STORAGE_ROOT/profiles/$PROFILE_ID/input/"
```

Ask the user (via plain text) whether to delete the original. Only delete if confirmed.

### 3b — Profile photo

Scan the profile input folder for existing image files:
```bash
find "$STORAGE_ROOT/profiles/$PROFILE_ID/input/" -maxdepth 1 \
  \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) \
  2>/dev/null | sort
```

Ask the user (via plain text) to choose from the image files found, provide a manual path, or skip the photo.

**If a file from the list is selected**: it is already in `input/` — no copy needed. Store its filename in `PHOTO_FILE`.

**If manual path is provided**: validate the file exists and has extension `.jpg`, `.jpeg`, `.png`, or `.webp`; if not, ask again. Copy to `input/` and ask whether to delete the original.

**If no photo**: set `PHOTO_FILE` to `null`.

---

## Step 4 — Extract profile data

Read the selected file and extract all available data following the schema structure:

- `metadata`: version=1.0, profile ID, source filename (`SOURCE_FILE`), timestamps
- `info`: name, titles array, contact (email, phone, location, others), photo (`PHOTO_FILE` — relative filename, or null)
- `languages`: array with level (native/fluent/intermediate/basic)
- `interests`: professional and personal interests
- `skills`: core competencies
- `knowledge`: categorized technical knowledge (category, key, values array)
- `experience`: array sorted descending by end date — position, company, location, period, description, responsibilities, achievements, technologies, team_size, industries
- `education`: type, category, title, institution, status, period
- `projects`: type (professional/personal), name, description, technologies, status, url

For missing or ambiguous fields ask the user (via plain text) to clarify — never invent data.

---

## Step 4b — Social networks and repositories

Social presence is a key credibility signal for ATS systems and recruiters. After extracting the CV data, explicitly collect professional network and repository links that may not appear in the document.

Show the user which links were already found in the CV (pre-fill), then ask the user (via plain text) to confirm or complete each tier:

**Tier 1 — Essential** (ask always):

| Type key | Platform | Example value |
|----------|----------|---------------|
| `linkedin` | LinkedIn profile | `https://linkedin.com/in/username` |
| `github` | GitHub profile | `https://github.com/username` |

**Tier 2 — High value for technical profiles** (ask always, skip if clearly non-applicable):

| Type key | Platform | Example value |
|----------|----------|---------------|
| `gitlab` | GitLab profile | `https://gitlab.com/username` |
| `stackoverflow` | Stack Overflow profile | `https://stackoverflow.com/users/id/username` |
| `portfolio` | Personal website / portfolio | `https://username.dev` |

**Tier 3 — Differentiators** (ask as a single optional multi-value question):

| Type key | Platform | When relevant |
|----------|----------|---------------|
| `medium` / `devto` / `hashnode` | Technical blog | Thought leadership roles |
| `credly` | Digital certifications badge profile | Certification-heavy profiles |
| `npm` / `pypi` | Package registry profile | Open source package authors |

Rules:
- Store each link in `contact.others` as `{type: "<type_key>", value: "<url>"}`.
- If a link was already found in the CV, show it and ask the user to confirm or correct it.
- Links left blank are simply not added — never store empty values.
- Accept only valid URLs; if the format looks wrong, ask again.

---

## Step 5 — Validate and save

Validate the resulting JSON against `$PLUGIN_CACHE/resources/schemas/profile.schema.json`.

If validation passes: save to `$STORAGE_ROOT/profiles/[user]/data/profile.json`.

If validation fails: report which fields are invalid and ask the user to correct them before saving.

---

## Step 6 — Confirm

Print summary:
```
✅ Profile saved: ~/.p4/p4-ccvv/profiles/[user]/data/profile.json
   Version: 1.0 | Experiences: N | Projects: N | Education: N
   Photo: [filename or "none"]
```
