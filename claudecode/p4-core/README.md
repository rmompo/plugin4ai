# p4-core

Core productivity plugin for Claude Code. Applies behavioral directives automatically and routes tasks to the right model tier via subagents.

## Behavioral Directives (P4D)

Active automatically when the plugin is installed — no setup required.

| ID | Directive |
|----|-----------|
| P4D-000 | Load directives from source at session start — never from memory |
| P4D-001 | Restricted actions require explicit confirmation — restriction restored immediately after |
| P4D-002 | Destructive actions forbidden without explicit authorization |
| P4D-003 | Consultation mode by default — execution requires explicit directive |
| P4D-004 | Git commits require unambiguous explicit instruction |
| P4D-005 | Clarify ambiguous input before acting |
| P4D-006 | Every factual claim must be verifiable — state uncertainty explicitly |
| P4D-007 | Evaluate independently before agreeing or validating |
| P4D-008 | Respond in the language of the user's last message |
| P4D-009 | Lists and comparable items must use structured, identified output |

Full spec: [`.project/rules.md`](./.project/rules.md)

---

## Skills

### 🔀 `model-route`

Evaluates task complexity and **delegates** to the right model tier via subagents.

| Agent | Model | Best for |
|-------|-------|----------|
| `p4-core:p4-lightweight` | **Haiku** | Quick lookups, file search, simple formatting |
| `p4-core:p4-standard` | **Sonnet** | General development, refactoring, PR reviews |
| `p4-core:p4-advanced` | **Opus** | Architecture design, complex debugging, critical decisions |

**Invocation:**
- Auto — activates when Claude detects complexity signals in the task
- Explicit — `/p4-core:model-route [task description]`

---

### 📝 `git-commit`

Generates and enforces [Conventional Commits](https://www.conventionalcommits.org/) on every commit.

- Interprets the user's intent (any language) and maps it to the correct type and scope
- **Always outputs in English**, regardless of input language
- **Never adds `Co-Authored-By:` lines**
- Subject ≤72 chars, imperative mood, no trailing period
- Breaking changes flagged with `!` and `BREAKING CHANGE:` footer

**Invocation:**
- Auto — activates whenever Claude is about to propose or execute a `git commit`
- Explicit — `/p4-core:git-commit [hint]`

**Examples:**

| Input | Output |
|-------|--------|
| `"arreglé el login"` | `fix(auth): resolve login failure on invalid credentials` |
| `"nueva pantalla de perfil"` | `feat(profile): add user profile screen` |
| *(staged changes, no hint)* | `feat(auth): add OAuth2 login with Google provider` |

---

### 🧠 `model-behaviour`

Loads and activates P4D behavioral directives for the session. Fires automatically at session start via the p4-core agent.

- Reads directives from the plugin cache — never from training memory
- Applies all P4D rules (P4D-000 through P4D-009) for the duration of the session
- Safe to re-invoke to reload updated directives

**Invocation:**
- Auto — fires at session start via the p4-core agent
- Explicit — `/p4-core:model-behaviour`

---

### 📋 `skill-list`

Lists all p4-* plugin skills installed in the current CLI, in a Markdown table with plugin, version, skill, tools status, and description columns.

- Reads from the CLI plugin cache — no network access
- Shows `✅` / `❌` in the `tools` column based on external dependency availability
- Collapses repeated plugin names for readability

**Invocation:**
- Explicit — `/p4-core:skill-list`

---

### 🔧 `setup`

Verifies that all external tools required by p4-core skills are installed and available in PATH. Reports status with install instructions for each missing dependency.

**Invocation:**
- Explicit — `/p4-core:setup`

---

## Installation

```bash
claude plugins marketplace add rmompo/plugin4ai
claude plugins install p4-core
```

No setup step required — behavioral directives activate automatically.

## Companion plugin

[`p4-claudecode`](../p4-claudecode/README.md) — visual enhancement with custom statusline (optional, Claude Code only).

## Port

This is the **Claude Code** port of the `p4-core` plugin.  
See [`ghcopilot/plugins/p4-core/`](../../../ghcopilot/plugins/p4-core/README.md) for the GitHub Copilot CLI adaptation.
