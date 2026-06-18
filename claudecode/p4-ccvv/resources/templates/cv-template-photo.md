---
type: curriculum-vitae
position: [POSITION]
metadata_id: [ID]
slug: [SLUG]
language: [LANGUAGE_CODE]
generated: [TIMESTAMP]
updated: [TIMESTAMP]
profile_version: [VERSION]
offer_analyzed: [BOOLEAN]
keywords: [ARRAY]
header-includes: |
  \usepackage{graphicx}
  \usepackage{array}
  \usepackage{hyperref}
  \hypersetup{colorlinks=true, urlcolor=blue}
---

\begin{table}[h]
\centering
\begin{tabular}{>{\centering\arraybackslash}m{4cm}>{\raggedright\arraybackslash}m{11cm}}
\includegraphics[width=3cm]{../../input/[PHOTO_FILE]} &
\textbf{\LARGE [FULL NAME]} \newline
\textit{[TITLE 1] | [TITLE 2] | [TITLE 3]} \newline
\smallskip
[EMAIL] \textbar{} [PHONE] \textbar{} [LOCATION] \newline
\href{[LINKEDIN_URL]}{LinkedIn}
\end{tabular}
\end{table}

\vspace{0.5cm}

---

<!-- SECTION: Professional Profile -->
## 1. [S_PROFESSIONAL_PROFILE]

[Tailored professional summary: years of experience, main domain, top competencies matching the position, and a closing sentence addressing the company's need if company context is available.]

**[S_KEY_SKILLS] [POSITION]:** [comma-separated skill list]

---

<!-- SECTION: Digital Identity — omit entire section if contact.others is empty -->
## 2. [S_DIGITAL_IDENTITY]

<!-- Include only platforms present in contact.others. Do not add empty lines. -->
- **GitHub**: [url]
- **GitLab**: [url]
- **Stack Overflow**: [url]
- **Portfolio**: [url]
- **Blog**: [url]
- **Credly**: [url]
- **NPM**: [url]
- **PyPI**: [url]

---

<!-- SECTION: Technical Stack -->
## 3. [S_TECHNICAL_STACK]

### 3.1. [CATEGORY NAME]

**[Subcategory]**: [comma-separated list]

**[Subcategory]**: [comma-separated list]

### 3.2. [CATEGORY NAME]

**[Subcategory]**: [comma-separated list]

### 3.3. [CATEGORY NAME]

**[Subcategory]**: [comma-separated list]

### 3.4. DevOps & Infrastructure

**Containers**: [tools]

**CI/CD**: [tools]

**Application Servers**: [servers]

### 3.5. [ADDITIONAL CATEGORY — only if applicable]

[Additional category content]

---

<!-- SECTION: Featured Projects -->
## 4. [S_FEATURED_PROJECTS]

<!-- Professional projects first (alphabetical), then personal (alphabetical) -->

### 4.1. [Professional Project Name]

**[S_DESCRIPTION]**: [project description]

**[S_TECHNOLOGIES]**:

- **[Category]**: [technologies]
- **[Category]**: [technologies]

[**URL**: [project url] — OPTIONAL, only if public]

---

### 4.X. [Personal Project Name] *(personal)*

**[S_DESCRIPTION]**: [project description]

**[S_TECHNOLOGIES]**:

- **[Category]**: [technologies]

[**URL**: [project url] — OPTIONAL]

---

<!-- SECTION: Professional Experience -->
## 5. [S_PROFESSIONAL_EXPERIENCE]

### 5.1. [Job Title] — [Company]

**[S_PERIOD]**: [START] – [END] | **[S_LOCATION]**: [location] | **[S_TEAM]**: [size] *(OPTIONAL)*

[Role description mirroring offer terminology]

**[S_RESPONSIBILITIES]**:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility N]

**[S_ACHIEVEMENTS]**: *(OPTIONAL)*
- [Achievement 1]
- [Achievement 2]

**[S_TECH_STACK]**: [comma-separated technologies]

---

<!-- SECTION: Education -->
## 6. [S_EDUCATION]

### 6.1. [Degree] — [Institution]

**[S_PERIOD]**: [START] – [END] | **[S_LOCATION]**: [location] | **[S_STATUS]**: [status]

[Additional information if applicable]

---

<!-- SECTION: Training & Certifications -->
## 7. [S_TRAINING_CERTIFICATIONS]

### 7.1. [Area]-[S_RELATED_TRAINING]

**[Course name]** — [Institution]

**[Course name]** — [Institution]

### 7.2. [S_OTHER_TRAINING]

**[Course name]** — [Institution]

---

<!-- SECTION: Languages & Interests -->
## 8. [S_LANGUAGES_INTERESTS]

### 8.1. [S_LANGUAGES]

- **[Language]**: [Level]
- **[Language]**: [Level]

### 8.2. [S_INTERESTS]

- [Interest 1]
- [Interest 2]
- [Interest N]

---


\begin{center}
[CLOSING PHRASE IN CV OUTPUT LANGUAGE]
\end{center}

<!-- GENERATION NOTES — not rendered in output -->
<!--
CV optimized for: [POSITION]

Keyword coverage:
- P1: [keyword list]
- P2: [keyword list]

Match score: [XX]%

Key strengths highlighted:
- [Strength 1]
- [Strength 2]
-->

<!-- END OF DOCUMENT -->
