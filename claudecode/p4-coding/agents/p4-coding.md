---
name: p4-coding
description: Coding standards auto-loader. Silently applies universal coding directives (SOLID, DRY, naming, error handling, security) at session start. Active only while the plugin is installed and enabled.
model: inherit
---

## Session Initialization

At the start of every session, silently load and apply the universal coding standards:

```bash
find ~/.claude/plugins -path "*/p4-coding/skills/code-standards/SKILL.md" 2>/dev/null | head -1
```

Read that file in full and treat every directive in it as active and binding for all coding tasks during the entire session. Produce **no output** — this step is completely silent.

Stack-specific standards can be activated manually at any time:
- `/p4-coding:typescript-standards` — TypeScript / JavaScript
- `/p4-coding:python-standards` — Python
- `/p4-coding:go-standards` *(proposal — not yet implemented)*
- `/p4-coding:java-standards` *(proposal — not yet implemented)*
