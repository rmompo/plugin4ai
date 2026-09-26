# p4-agent

> **Status:** `beta`

Agent definition auditor: validates markdown agent files for structural completeness, naming conventions, and cross-reference integrity.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `md-check` | `/p4-agent:md-check` | Audits a single agent markdown file for structural completeness and naming conventions. |
| `md-checkrefs` | `/p4-agent:md-checkrefs` | Audits an agent markdown file and all files it references, checking cross-reference integrity. |

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-agent
```
