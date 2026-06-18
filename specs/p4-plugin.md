# Plugin Spec: p4-plugin

> **Status:** `beta` | **Version:** `1.1.26` | **Ports:** Claude Code only

## Overview

`p4-plugin` provides full lifecycle management for the plugin4ai marketplace. It handles creation, modification and removal of plugins and skills, keeping all catalogs and the CLI cache in sync automatically after every operation.

`specs/catalog.json` is the primary source of truth — all operations write there first and derive all other files from it.

---

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `create` | `/p4-plugin:create <plugin> [skills...]` | Scaffold a new plugin with all required files |
| `update` | `/p4-plugin:update <plugin>` | Update plugin metadata (description, status, ports) |
| `remove` | `/p4-plugin:remove <plugin>` | Remove a plugin from all files and cache |
| `skill-add` | `/p4-plugin:skill-add <plugin> <skill>` | Add a new skill to an existing plugin |
| `skill-update` | `/p4-plugin:skill-update <plugin> <skill>` | Bump skill version and update changelogs |
| `skill-remove` | `/p4-plugin:skill-remove <plugin> <skill>` | Remove a skill from a plugin |
| `skill-doctor` | `/p4-plugin:skill-doctor [plugin] [skill]` | Audit skills for defects and inconsistencies |
| `doc-doctor` | `/p4-plugin:doc-doctor [plugin]` | Audit documentation completeness across specs and MARKETPLACE.md |

---

## Files updated per operation

| File | create | update | remove | skill-add | skill-update | skill-remove |
|------|--------|--------|--------|-----------|--------------|--------------|
| `specs/catalog.json` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `claudecode/<plugin>/.claude-plugin/plugin.json` | ✅ | ✅* | ❌ deleted | ✅ | ✅ | — |
| `.claude-plugin/marketplace.json` | ✅ | ✅* | ✅ | — | — | — |
| `claudecode/MARKETPLACE.md` | ✅ | ✅* | ✅ | — | — | — |
| `specs/<plugin>.md` | ✅ | — | ❌ deleted | — | — | — |
| `claudecode/<plugin>/skills/<skill>/SKILL.md` | ✅ | — | — | ✅ created | ✅ bumped | ❌ deleted |
| CLI cache | ✅ | ✅* | ❌ deleted | ✅ | ✅ | ✅ |

*only if version or description changed

---

## Version management — Z system

Plugin version is `X.Y.Z`:
- `X` — major: breaking changes
- `Y` — minor: new features or significant behaviour changes
- `Z` — monotonic skill counter: **never resets**, even when X or Y change

`Z` always equals the highest skill version ever assigned in the plugin.

| Event | Z |
|-------|---|
| `skill-add` | Z + 1 (new skill gets this value) |
| `skill-update` | Z + 1 (updated skill gets this value) |
| `skill-remove` | unchanged (monotonic) |
| `update` metadata | unchanged |

---

## Destructive operations

`remove` and `skill-remove` require explicit confirmation via `AskUserQuestion` before proceeding.

---

## Non-Goals

- Does not push to git (`git add + commit + push` is a manual next step)
- Does not install plugins in other consoles (`claude plugins update <plugin>` still required)
- Does not fill in skill logic — only scaffolds the structure

---

## Port Status

| CLI | Location | Status |
|-----|----------|--------|
| Claude Code | `claudecode/p4-plugin/` | ✅ Beta |
| GitHub Copilot CLI | — | 🔶 Proposal |
| Gemini CLI | — | 🔶 Proposal |
| Codex CLI | — | 🔶 Proposal |

## Changelog

| Version | Changes |
|---------|---------|
| 1.1.9 | Split manage into 6 independent skills: create, update, remove, skill-add, skill-update, skill-remove |
| 1.0.3 | manage: full lifecycle rewrite — catalog-first sync, cache sync |
| 1.0.2 | manage: update plugin.json template with skills/changelog structure |
| 1.0.1 | Rename create→manage; add lifecycle operations and Z versioning |
| 1.0.0 | Initial release with create skill |
