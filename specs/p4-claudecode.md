# Plugin Spec: p4-claudecode

> **Status:** `stable` | **Version:** `1.0.2` | **Ports:** Claude Code CLI/TUI only

## Overview

`p4-claudecode` is a Claude Code CLI/TUI-exclusive visual enhancement plugin. It replaces the default statusline with a custom color-coded bar that surfaces project context, git state, active model and usage metrics at a glance.

It is intentionally decoupled from `p4-core` — it can be installed standalone or alongside any other plugin.

---

## Skill: `statusline`

### Purpose

Install the statusline script and activate it in Claude Code CLI/TUI's settings. Runs automatically at session start via the plugin's default agent. The `/p4-claudecode:statusline` skill is available as a manual fallback or for reinstallation.

### Invocation

```bash
/p4-claudecode:statusline    # manual install or reinstall
```

### Auto-setup behavior

The `p4-claudecode` agent (activated via `settings.json`) checks at session start:

1. Is `~/.claude/statusline-command.sh` present and matches the plugin source?
2. Does `~/.claude/settings.json` have `statusLine` pointing to it?

If all conditions are met → silent, no action.
If any condition fails → installs/updates automatically and reports briefly.

### Statusline output

```
⌂ ~/your/project  ⎇ main  ✦ claude-sonnet-4-5  CX:16% SN:88% WK:8%
```

| Segment | Color | Source |
|---------|-------|--------|
| `⌂ path` | Yellow | `workspace.project_dir`, home-collapsed |
| `⎇ branch` | Cyan | Git branch / worktree name |
| `✦ model` | Purple | `model.display_name` |
| `CX:%` | Green/Yellow/Red | `context_window.used_percentage` |
| `SN:%` | Green/Yellow/Red | `rate_limits.five_hour.used_percentage` |
| `WK:%` | Green/Yellow/Red | `rate_limits.seven_day.used_percentage` |

Color thresholds: ≤40% green · ≤75% yellow · >75% red.

### Non-Goals
- Does not port to other CLIs (no statusline API available)
- Does not modify any project files
- Does not affect Claude's behavior or responses

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code CLI/TUI | `claudecode/p4-claudecode/` | ✅ Stable |
| GitHub Copilot CLI/TUI | — | ❌ Not applicable |
| Antigravity CLI/TUI | — | ❌ Not applicable |
| Codex CLI/TUI | — | ❌ Not applicable |

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.1 | Version alignment to Z system |
| 1.0.0 | Initial release — renamed from p4-statusline, skill setup→statusline |
