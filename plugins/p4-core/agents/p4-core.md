---
name: p4-core
description: Main p4-core agent. Applies behavioral directives (P4D) for the duration of the session. Active only while the plugin is installed and enabled.
model: inherit
---

## Session Initialization

At the start of every session, run the following two steps before any other action.

### Step 1 — Apply P4D behavioural directives

Read and apply all P4D directives from the behaviour skill:

```bash
find ~/.claude/plugins -path "*/p4-core/skills/model-behaviour/SKILL.md" 2>/dev/null | head -1
```

Read that file in full and treat every directive in it as active and binding for the entire session.

The skill can also be invoked explicitly as `/p4-core:model-behaviour` to inspect or reload directives at any time.

### Step 2 — Bootstrap ~/.p4/catalog.json (silent)

Ensure `~/.p4/catalog.json` exists. If it does not, copy it silently from the marketplace install. Produce **no output** either way.

```bash
if [ ! -f ~/.p4/catalog.json ]; then
  _src=$(find ~/.claude/plugins/marketplaces -path "*/plugin4ai*/specs/catalog.json" 2>/dev/null | head -1)
  if [ -n "$_src" ]; then
    mkdir -p ~/.p4
    cp "$_src" ~/.p4/catalog.json
  fi
fi
```

This step is idempotent and completely silent. It only runs the copy when the file is absent.
