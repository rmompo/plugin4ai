---
name: generate
description: Generates an adapted CV draft for a specific job position. Analyzes the job offer, extracts keywords, and creates a markdown draft ready for review and export. Also invoked explicitly as /p4-ccvv:generate.
version: 14
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# Generate CV

Creates a CV draft optimized to achieve **>95% match score** as an ideal candidate for a specific job position. When a job offer is provided, every section of the CV is generated and validated against a prioritized keyword blueprint extracted from the offer.

```
STORAGE_ROOT     = ~/.p4/p4-ccvv
GUIDELINES       = <plugin-cache>/resources/CV-GENERATION-GUIDELINES.md
TEMPLATE_PHOTO   = <plugin-cache>/resources/templates/cv-template-photo.md
TEMPLATE_NOPHOTO = <plugin-cache>/resources/templates/cv-template-nophoto.md
```

---

## Step 1 — Select user

Read `profiles.json`. Use **AskUserQuestion** to select the profile.

Verify `profile.json` exists. If not, suggest `/p4-ccvv:profile-gather` first.

---

## Step 2 — Collect generation parameters

Use **AskUserQuestion** to collect:

1. Target job position (mandatory)
2. Job offer text (optional — paste the full offer for keyword extraction and score optimization)
3. Company name (optional)
4. Cover letter needed? (yes/no)
5. Output language: `es` / `en` / `fr` / `de` / `it` / `pt` (default: `es`)

---

## Step 3 — Prepare metadata

Read `cvs.json` (create if absent). Calculate new metadata ID = `max(existing ids) + 1` (start at 1).

Generate slug from position: lowercase, spaces → underscores, remove special chars.

Create output folder: `$STORAGE_ROOT/profiles/[user]/output/CV-[id_padded]-[slug]/`

---

## Step 4 — Offer analysis and keyword blueprint

**If no offer text provided**: set `offer_analyzed: false`, `keywords: []`, `keyword_blueprint: null`. Skip to Step 4b — title adaptation will be based on position name only.

**If offer text provided**, perform a full analysis to build the keyword blueprint that will drive all subsequent content decisions:

### 4.1 — Extract keywords and phrases

Extract all relevant terms from the offer at two levels:

- **Single keywords**: technical skills, tools, frameworks, methodologies, domain terms, soft skills
- **Multi-word phrases**: extract verbatim phrases that appear as units in the offer (e.g. "distributed systems", "continuous integration", "gestión de equipos", "cloud-native architecture"). These must be placed as-is in the CV — never paraphrased.

Filter out: articles, prepositions, generic corporate filler ("dynamic team", "fast-paced environment").

### 4.2 — Assign priority tiers

Score each keyword/phrase by its weight in the offer:

| Tier | Criteria | Coverage requirement |
|------|----------|----------------------|
| **P1** | Appears in the job title, mandatory requirements section, or 3+ times in the offer | Must appear in ≥2 different CV sections, including the professional profile |
| **P2** | Appears in preferred/valued skills, or 2 times in the offer | Must appear in ≥1 CV section |
| **P3** | Appears once, in nice-to-have or company description | At least 1 occurrence anywhere in the CV if supported by the profile |

### 4.3 — Implicit keyword expansion

For each P1 and P2 keyword, identify related terms already present in `profile.json` that reinforce the same competency and should co-occur in the CV (e.g. offer says "cloud" → profile has AWS + GCP → both appear; offer says "agile" → profile has Scrum + Kanban → both surface).

### 4.4 — Anti-dilution filter

Identify profile content (projects, technologies, responsibilities) that has zero keyword overlap with the offer. This content dilutes the relevance score and must be:
- **Omitted** if it adds no signal for this position
- **Relegated** to a minor mention if removing it would create an unexplained gap

### 4.5 — Build keyword blueprint

Produce a structured artifact:

```
KEYWORD BLUEPRINT
=================
Position title (verbatim): [exact title from offer]

P1 keywords/phrases: [list with target section placement]
P2 keywords/phrases: [list]
P3 keywords/phrases: [list]

Implicit expansions: [keyword → [related terms from profile]]
Content to omit/relegate: [list]
```

This blueprint is the reference for all content decisions in Steps 4b and 5.

---

## Step 4b — Adapt titles to position

From `info.titles` in `profile.json`, derive the 1–3 titles that best represent the candidate **for this specific position**. Store the result as `adapted_titles: string[]` — this replaces `info.titles` verbatim in the generated CV header.

Rules (apply in order):

1. **Mirror the offer's job title first** — if the offer's exact position title (or a close variant) can be honestly claimed given the profile, place it first.
2. **Exact / near match from profile** — map remaining profile titles to what the offer signals as valued.
3. **Filter irrelevant titles** — omit titles that don't add value for this role (e.g. drop "Fullstack SR Developer" for a pure Backend or Architecture position; drop "Tech Lead" for an individual-contributor role).
4. **Construct a position-derived title if needed** — only if it genuinely reflects the candidate's background. Never assign a role they haven't held.
5. **Max 3 titles** (template constraint). Prefer fewer, more precise titles over three generic ones.
6. **Preserve seniority signals** relevant to the role (SR, Lead, Architect…).

---

## Step 5 — Generate CV draft (keyword-guided)

### 5.0 — Select template and resolve section labels

**Template selection** — based on `info.photo` in `profile.json`:
- `info.photo` is a filename → use `TEMPLATE_PHOTO`. Replace `[PHOTO_FILE]` with the filename.
- `info.photo` is null → use `TEMPLATE_NOPHOTO`.

**Section label translation** — the templates use `[S_*]` placeholders for section and field names. Resolve each placeholder to the CV output language set in Step 2:

| Placeholder | es | en | fr | de | it | pt |
|---|---|---|---|---|---|---|
| `[S_PROFESSIONAL_PROFILE]` | PERFIL PROFESIONAL | PROFESSIONAL PROFILE | PROFIL PROFESSIONNEL | BERUFSPROFIL | PROFILO PROFESSIONALE | PERFIL PROFISSIONAL |
| `[S_DIGITAL_IDENTITY]` | IDENTIDAD DIGITAL | DIGITAL IDENTITY | IDENTITÉ NUMÉRIQUE | DIGITALE IDENTITÄT | IDENTITÀ DIGITALE | IDENTIDADE DIGITAL |
| `[S_TECHNICAL_STACK]` | STACK TECNOLÓGICO | TECHNICAL STACK | STACK TECHNIQUE | TECHNISCHER STACK | STACK TECNOLOGICO | STACK TECNOLÓGICO |
| `[S_FEATURED_PROJECTS]` | PROYECTOS DESTACADOS | FEATURED PROJECTS | PROJETS PHARES | AUSGEWÄHLTE PROJEKTE | PROGETTI PRINCIPALI | PROJETOS DESTACADOS |
| `[S_PROFESSIONAL_EXPERIENCE]` | EXPERIENCIA PROFESIONAL | PROFESSIONAL EXPERIENCE | EXPÉRIENCE PROFESSIONNELLE | BERUFSERFAHRUNG | ESPERIENZA PROFESSIONALE | EXPERIÊNCIA PROFISSIONAL |
| `[S_EDUCATION]` | EDUCACIÓN | EDUCATION | FORMATION | BILDUNG | ISTRUZIONE | EDUCAÇÃO |
| `[S_TRAINING_CERTIFICATIONS]` | FORMACIÓN Y CERTIFICACIONES | TRAINING & CERTIFICATIONS | FORMATION ET CERTIFICATIONS | FORTBILDUNG & ZERTIFIZIERUNGEN | FORMAZIONE E CERTIFICAZIONI | FORMAÇÃO E CERTIFICAÇÕES |
| `[S_LANGUAGES_INTERESTS]` | IDIOMAS E INTERESES | LANGUAGES & INTERESTS | LANGUES ET INTÉRÊTS | SPRACHEN & INTERESSEN | LINGUE E INTERESSI | IDIOMAS E INTERESSES |
| `[S_KEY_SKILLS]` | Habilidades destacadas para | Key skills for | Compétences clés pour | Schlüsselkompetenzen für | Competenze chiave per | Habilidades-chave para |
| `[S_DESCRIPTION]` | Descripción | Description | Description | Beschreibung | Descrizione | Descrição |
| `[S_TECHNOLOGIES]` | Tecnologías | Technologies | Technologies | Technologien | Tecnologie | Tecnologias |
| `[S_PERIOD]` | Período | Period | Période | Zeitraum | Periodo | Período |
| `[S_LOCATION]` | Ubicación | Location | Lieu | Standort | Sede | Localização |
| `[S_TEAM]` | Equipo | Team | Équipe | Team | Team | Equipe |
| `[S_RESPONSIBILITIES]` | Responsabilidades | Responsibilities | Responsabilités | Aufgaben | Responsabilità | Responsabilidades |
| `[S_ACHIEVEMENTS]` | Logros | Achievements | Réalisations | Erfolge | Risultati | Conquistas |
| `[S_TECH_STACK]` | Stack Tecnológico | Tech Stack | Stack Technique | Technologie-Stack | Stack Tecnologico | Stack Tecnológico |
| `[S_STATUS]` | Estado | Status | Statut | Status | Stato | Estado |
| `[S_RELATED_TRAINING]` | Relacionada con | Related Training | Liée à | Bezogene Ausbildung | Correlata a | Relacionada com |
| `[S_OTHER_TRAINING]` | Otra Formación | Other Training | Autre Formation | Weitere Ausbildung | Altra Formazione | Outra Formação |
| `[S_LANGUAGES]` | Idiomas | Languages | Langues | Sprachen | Lingue | Idiomas |
| `[S_INTERESTS]` | Intereses Profesionales y Personales | Professional & Personal Interests | Intérêts Professionnels et Personnels | Berufliche und persönliche Interessen | Interessi Professionali e Personali | Interesses Profissionais e Pessoais |

### Section ordering

Reorder sections to front-load what the offer emphasizes most:
- If the offer is heavily technical → STACK TECNOLÓGICO before PROYECTOS DESTACADOS
- If the offer emphasizes leadership or methodology → surface those signals early in PERFIL PROFESIONAL and EXPERIENCIA
- Default order if no offer or offer is balanced:
  1. PROFESSIONAL PROFILE
  2. DIGITAL IDENTITY *(omit if no entries in contact.others)*
  3. TECHNICAL STACK
  4. FEATURED PROJECTS
  5. PROFESSIONAL EXPERIENCE
  6. EDUCATION
  7. TRAINING & CERTIFICATIONS
  8. LANGUAGES & INTERESTS

### Content rules (apply to every section)

- **Verbatim placement**: P1 and multi-word phrases must appear verbatim — never paraphrase or use synonyms.
- **Action verb mirroring**: use the same action verbs the offer uses (if the offer says "diseñar", the CV says "diseñar", not "crear" or "desarrollar").
- **Quantification**: always surface numbers from the profile — team sizes, durations, percentages, scale indicators. Quantified statements score higher with both ATS and AI screeners.
- **P1 multi-section coverage**: each P1 keyword must appear in at least 2 sections. Place the first occurrence in PERFIL PROFESIONAL.
- **Keyword density without stuffing**: distribute naturally across sentences; avoid repeating the same keyword more than once per paragraph.
- **Anti-dilution**: apply the filter from Step 4.4 — omit or relegate low-relevance content.

### Section-specific guidance

**DIGITAL IDENTITY** (`[S_DIGITAL_IDENTITY]`)
- Include this section only if `contact.others` in `profile.json` has at least one entry.
- List only the platforms that are present — never add empty or placeholder lines.
- Format each entry as: `- **[Platform name]**: [url]`
- Order: GitHub → GitLab → Stack Overflow → Portfolio → Blog → Credly → NPM → PyPI
- Omit the entire section (and its number) if `contact.others` is empty; renumber subsequent sections accordingly.

**PROFESSIONAL PROFILE** (`[S_PROFESSIONAL_PROFILE]`)
- Open with the offer's exact position title (or `adapted_titles[0]`) in the first sentence.
- Cover all P1 keywords within this section.
- Reference years of experience, primary domain, and top 3 technical competencies matching the offer.
- Close with a sentence that directly addresses the company's need as stated in the offer (if company name and offer context available).

**STACK TECNOLÓGICO**
- Lead with the categories most relevant to the offer.
- Within each category, list P1 and P2 keywords first.
- Include implicit expansions from Step 4.3.
- Omit technologies with no overlap with the offer unless they are core to the candidate's identity.

**PROYECTOS DESTACADOS**
- Select only projects with keyword overlap with the offer.
- Rewrite descriptions to surface P1/P2 keywords naturally.
- Professional projects first, then personal; alphabetical within each group.

**EXPERIENCIA PROFESIONAL**
- Descending by end date.
- For each position: rewrite responsibilities and achievements to mirror the offer's action verbs and terminology.
- Surface quantifications (team size, scope, impact).
- Omit responsibilities with no relevance to the offer.

**EDUCACIÓN / FORMACIÓN / CERTIFICACIONES**
- Include only if relevant to the position or if a P2/P3 keyword appears here.

**IDIOMAS E INTERESES**
- Always include languages.
- Interests: include only if they resonate with the offer's domain or company culture signals.

### Cover letter (if requested)

Use the cover letter as a strategic overflow for P2/P3 keywords that could not be placed naturally in the CV. Structure: hook referencing the exact position title → candidate's value proposition → 2-3 specific matches to the offer's requirements → call to action.

Save draft as: `CV-[id_padded]-META-[slug]-CV.md`
Save cover letter as: `CV-[id_padded]-META-[slug]-LETTER.md`

---

## Step 6 — Two-pass validation and score estimation

**Only when offer text was provided.** This step ensures the generated draft meets the >95% target before saving.

### Pass 1 — Keyword coverage check

For each keyword/phrase in the blueprint, verify its presence and tier compliance in the draft:

```
P1 "[keyword]" → found in: [sections] | coverage: ✅ / ⚠️ insufficient / ❌ missing
P2 "[keyword]" → found in: [sections] | coverage: ✅ / ⚠️ / ❌
P3 "[keyword]" → found: ✅ / ❌
```

### Pass 2 — Gap patching

For every ⚠️ or ❌ finding:
- Identify the most natural section to add or reinforce the keyword
- Rewrite the minimum necessary text to achieve coverage without forcing
- Re-verify after patching

### Score estimation

```
score = Σ(covered_keywords × tier_weight) / Σ(all_keywords × tier_weight)

Tier weights: P1 = 3, P2 = 2, P3 = 1
```

If `score < 0.95`: perform an additional patch pass targeting the lowest-scoring P1/P2 items. Repeat until score ≥ 0.95 or no further natural placement is possible (flag remaining gaps).

---

## Step 7 — Update cvs.json

Append new metadata entry including `match_score` and `keyword_blueprint` summary. Update `info.total_metadata`, `info.last_generated`.

---

## Step 8 — Confirm

```
✅ CV draft generated: CV-[id_padded]-META-[slug]-CV.md
   Position : [position]
   Keywords : P1: N | P2: N | P3: N
   Match score: XX% (target: >95%)
   Offer analyzed: yes/no

Next steps:
  1. Review and edit the draft
  2. Run /p4-ccvv:export to produce PDF/DOCX/HTML
```
