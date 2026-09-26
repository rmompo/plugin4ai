# p4-claudecode

Visual enhancement plugin for Claude Code. Replaces the default statusline with a color-coded bar showing project context, git branch, active model and usage metrics.

## Result

```
[~/your/project] · [⎇ main] · Sonnet 4.6 · cx:16% sn:88% wk:8%
```

| Segment | Color | Description |
|---------|-------|-------------|
| `[~/path]` | 🟡 Yellow | Project directory, home collapsed to `~` |
| `[⎇ branch]` | 🔵 Cyan | Current git branch / worktree |
| `Model` | 🟠 Orange | Active model display name |
| `cx:%` | 🟢/🟡/🔴 | Context window usage |
| `sn:%` | 🟢/🟡/🔴 | 5-hour session rate limit |
| `wk:%` | 🟢/🟡/🔴 | 7-day weekly rate limit |

Usage values are colored by threshold: green (≤40%) · yellow (≤75%) · red (>75%).

## Skills

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| `setup` | `/p4-claudecode:setup` · once after install | Installs script and activates statusline |

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-claudecode
/p4-claudecode:setup
```

## Notes

- Claude Code only — GitHub Copilot CLI has no statusline API.
- Pairs well with [`p4-core`](../p4-core/README.md) but works standalone.
