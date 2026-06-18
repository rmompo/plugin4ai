---
name: gcomp
description: Generates a <hr-platform> mission report from the active project or a user hint. Infers all fields automatically and confirms each section before finalizing. Also invoked explicitly as /p4-buddy:gcomp with an optional project description hint.
---

# <hr-platform> Mission Generator (GitHub Copilot)

Generates a ready-to-paste `<hr-platform>` mission report for an `<company>` employee.

---

## Behavior

- **With argument** (`/p4-buddy:gcomp <hint>`): use the hint as primary source, complement with workspace context.
- **Without argument**: analyze the active workspace (git log, README, file structure) and infer all fields.
- In both cases: infer as much as possible, then **confirm each section with the user** before showing the final report.

---

## Step 0 — Locate repo root

```bash
git rev-parse --show-toplevel 2>/dev/null
```

---

## Step 1 — Gather context

### From workspace (always run these):
```bash
# Project name and recent activity
git log --oneline -20

# README or project description
cat README.md 2>/dev/null || cat CLAUDE.md 2>/dev/null || true

# Tech stack clues
ls
cat pom.xml 2>/dev/null | head -60 || cat package.json 2>/dev/null | head -40 || true
```

### From hint (if provided):
Extract: client name, project name, technologies, role, dates, activities.

---

## Step 2 — Infer all fields

Build a draft for each field using the gathered context:

### Section 1 — Project Description

| Field | How to infer |
|-------|-------------|
| **Client** | From hint, git remote URL, README, or ask |
| **Location** | Default to `<default-location>` unless hint says otherwise |
| **Project name** | Short and synthetic — from repo name, README title, or hint. Max 60 chars, no verbose. |
| **Description** | Follow the exact hierarchical bullet format (see below) |

**Description format** (mandatory — copy this syntax exactly):
```
* Sector
** Descripción del Proyecto
*** Punto clave 1
*** Punto clave 2
** Otro aspecto
*** Detalle
```

Infer sector from the domain (e.g. "Tecnología y Sistemas de Información", "Banca", "Administración Pública", "Salud", etc.).

### Section 2 — Mission Participation

| Field | How to infer |
|-------|-------------|
| **Role** | From hint or commit patterns. Common values: `Desarrollador`, `Arquitecto`, `Tech Lead`, `Ingeniero Prompting`, `Consultor`, `Analista`, `DevOps` |
| **Start date** | From git log first commit date or hint (format: MM/AAAA) |
| **End date** | If project is active → leave blank and mark `actualmente` |
| **Activities** | From git log, README, hint — use hierarchical bullet format (see below) |
| **Technical competencies** | Match technologies found against the catalog (see below) — only use exact catalog values |

**Activities format** (mandatory — copy this syntax exactly):
```
* Tarea principal 1
** Subtarea 1.1
*** Detalle 1.1.1
** Subtarea 1.2
* Tarea principal 2
** Subtarea 2.1
```

---

## Step 3 — Confirm section by section

Present each section to the user separately using `AskUserQuestion` before moving to the next.

**Do NOT show the full report at once.** Follow this sequence:

### Confirmation 1 — Project Description
Display the drafted Section 1 fields, then ask:
- question: `"¿Es correcta la descripción del proyecto?"`
- header: `"Sección 1"`
- options: `["Sí, continuar", "Necesito hacer cambios"]`

If the user selects "Necesito hacer cambios": ask a follow-up with a free-text prompt, apply corrections, then re-confirm.

### Confirmation 2 — Mission Participation
Display the drafted Section 2 fields, then ask:
- question: `"¿Son correctas las responsabilidades y actividades?"`
- header: `"Sección 2"`
- options: `["Sí, continuar", "Necesito hacer cambios"]`

If the user selects "Necesito hacer cambios": ask a follow-up, apply corrections, then re-confirm.

### Confirmation 3 — Technical Competencies
Display the inferred competency list, then ask:
- question: `"¿Son correctas las competencias técnicas? Deben pertenecer al catálogo <hr-platform>."`
- header: `"Competencias"`
- options: `["Sí, generar informe", "Necesito hacer cambios"]`

If the user selects "Necesito hacer cambios": ask a follow-up, apply corrections, then re-confirm.

---

## Step 4 — Final report

Once all sections are confirmed, output the complete mission report in this format:

```
═══════════════════════════════════════════════════
  MISIÓN <HR-PLATFORM> — LISTA PARA COPIAR
═══════════════════════════════════════════════════

## 1. DESCRIPCIÓN DEL PROYECTO

Cliente:          <value>
Ubicación:        <value>
Nombre proyecto:  <value>
Mi empresa:       <company>

Descripción:
<hierarchical bullets>

═══════════════════════════════════════════════════

## 2. PARTICIPACIÓN EN LA MISIÓN

Papel:            <value>
Fecha inicio:     <value>
Fecha fin:        <value or "Actualmente">

Actividades realizadas:
<hierarchical bullets>

Contexto de misión (competencias técnicas):
<one competency per line, exact catalog values>

═══════════════════════════════════════════════════
```

---

## Technical Competencies Catalog

Only select values from this list. Never invent competencies not in the catalog.

```
.Net, 3Ds max, ActiveMQ, Adobe Indesign, Adobe Photoshop, Ajax, Alfresco,
Angular, Ant, ArgoUML, Arquitectura-Software, Atom, Axis - Webservices,
Bitbucket, Blender, Bootstrap, Brackets, Cognos, Confluence, Copilot 365,
Crystal Reports, CSS, CSS 3, Data modeler, DB2, DBase, DBeaver, Docker,
Domino Workflow, draw.io, Eclipse, Eclipse UML, ExtJS,
GenAI Playground / Hub, GeoServer, Gimp (GNU Image Manipulation Program),
Git, Github Copilot, GitLab, Hibernate, HSQLDB, HTML, HTML 5, Informix,
IntelliJ, IReport, Jasper Report, Java, Javascript, Jenkins, Jira, JMeter,
JPA, jQuery, JSTL, JUnit, Keepass, Large Language Models (LLM), LibreOffice,
Mantis, MariaDB, Maven, Microsoft Access, Microsoft Excel, Microsoft OneNote,
Microsoft Outlook, Microsoft PowerPoint, Microsoft Project, Microsoft Teams,
Microsoft Visio, Microsoft Word, MongoDB, MySQL, MySQL Workbench,
Nginx (Web server), Notepad ++, Office 365, Oracle, Oracle Application Server,
Oracle applications, Oracle Data Miner, Oracle Designer, Oracle Forms Reports,
Oracle golden gate, Oracle JDeveloper, Oracle OC4J, Oracle SQL Developer,
Oracle SQL Developer Data Modeler, Oracle VM,
OWB - Oracle Warehouse Builder, Paquete Office, Pencil, PHP, PHP MyAdmin,
PL-SQL, PostgreSQL, PostMan, PowerBuilder,
PowerDesigner (ex PowerAMC), Putty, Python, Raspberry Pi, Redmine,
Retrieval Augmented Generation (RAG), Silverlight, Skype for Business,
SoapUI, SonarQube, Sound Forge, Sourcetree, Spring, Spring Boot,
Spring Data, Spring MVC, Spring Security, Spring Web Flow, SQL, SQL*Loader,
SQLite, SQLServer, Squirrel, Ssh-Secure Shell, StarUML, Struts,
Sublime Text, Sybase, TOAD, VBA - Visual Basic for Applications,
Virtual Box, VirtualBox, Visual Basic, Visual Basic .Net, Visual Studio,
Visual Studio Code, VMware, VSS - Visual SourceSafe, Web Services,
WinMerge, WinScp, Wordpress, XML, XML Spy, XQuery, XSL, Zoom
```
