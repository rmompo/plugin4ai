# Plugin Spec: p4-buddy

> **Status:** `beta` | **Version:** `1.0.2` | **Ports:** Claude Code CLI/TUI, GitHub Copilot CLI/TUI, Antigravity CLI/TUI, Codex CLI/TUI

---

## Overview

`p4-buddy` is a collection of skills for <company> employees using Claude Code CLI/TUI. It provides tooling for internal <company> platform workflows, starting with <hr-platform> mission reporting.

Works standalone — no dependency on `p4-core` or `p4-claudecode`.

---

## Port Status

| CLI/TUI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-buddy/` | ✅ Beta |
| GitHub Copilot CLI/TUI | `ghcopilot/plugins/p4-buddy/` | ✅ Beta |
| Antigravity CLI/TUI | `antigravity/p4-buddy/` | ✅ Beta |
| Codex CLI/TUI | `codex/p4-buddy/` | ✅ Beta |

---

## Skill: `gcomp`

### Purpose

Generate a ready-to-paste <hr-platform> mission report for an <company> employee, inferring all fields automatically from the active workspace or a user-provided hint, and confirming each section interactively via `AskUserQuestion` before producing the final output.

### Invocation

```bash
/p4-buddy:gcomp                              # auto-infer from active workspace
/p4-buddy:gcomp <project-hint>               # with a project hint
```

### Input sources (priority order)

1. User hint (if provided as argument)
2. Active workspace: `git log`, `CLAUDE.md`, `README.md`, `pom.xml` / `package.json`

### Mission structure

#### Section 1 — Project Description

| Field | Notes |
|-------|-------|
| Client | Name of the client organization |
| Location | Country — defaults to `España` |
| Project name | Short and synthetic, max ~60 chars |
| My company | Always `<company>` |
| Description | Hierarchical bullets: `*` sector · `**` project · `***` key points |

#### Section 2 — Mission Participation

| Field | Notes |
|-------|-------|
| Role | e.g. Desarrollador, Arquitecto, Ingeniero Prompting |
| Start date | MM/AAAA — inferred from first git commit or hint |
| End date | MM/AAAA — blank + `actualmente` if ongoing |
| Activities | Hierarchical bullets: `*` task · `**` subtask · `***` detail |
| Technical competencies | Must match exact values from the 145-entry catalog |

### Interaction flow

Uses `AskUserQuestion` to confirm sections one at a time — never dumps the full report at once:

1. Draft Section 1 → **AskUserQuestion** confirm → apply corrections if needed
2. Draft Section 2 (role, dates, activities) → **AskUserQuestion** confirm → apply corrections
3. Draft competencies → **AskUserQuestion** confirm → apply corrections
4. Output final formatted report

### Competency catalog

145 official competencies embedded in `SKILL.md`. The skill only selects values from this catalog — no invented entries.

### Output format

```
═══════════════════════════════════════════════════
  MISIÓN GCOMP — LISTA PARA COPIAR
═══════════════════════════════════════════════════

---

## 1. DESCRIPCIÓN DEL PROYECTO

Cliente:          <value>
Ubicación:        <value>
Nombre proyecto:  <value>
Mi empresa:       <company>

Descripción:
* Sector
** Descripción del proyecto
*** Punto clave

═══════════════════════════════════════════════════

---

## 2. PARTICIPACIÓN EN LA MISIÓN

Papel:            <value>
Fecha inicio:     MM/AAAA
Fecha fin:        MM/AAAA | Actualmente

Actividades realizadas:
* Tarea principal
** Subtarea

Contexto de misión (competencias técnicas):
<one per line, exact catalog values>

═══════════════════════════════════════════════════
```

### Non-Goals
- Does not submit data to <hr-platform> automatically (copy-paste only)
- Does not access the <hr-platform> API
- Does not store employee personal data

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.2 | gcomp: use AskUserQuestion for interactive section confirmations |
| 1.0.1 | Add gcomp skill |
| 1.0.0 | Initial release |
