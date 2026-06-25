---
name: model-route
description: This skill should be used when Claude needs to route a task to the most appropriate model tier. Activates automatically when Claude detects task complexity signals that suggest a different model would be more appropriate. Also invoked explicitly as /p4-core:model-route with an optional task description.
version: 30
argument-hint: "[task description]"
allowed-tools: [Bash]
---

# Model Routing — Task Delegation to the Right Model

This skill evaluates the current task and delegates it to the appropriate p4-core agent, which runs on the model best suited for the complexity and stakes involved.

## Routing Decision Matrix

### 🟢 Lightweight — delegate to `p4-core:p4-lightweight` (Haiku)
**Use when the task involves:**
- Simple questions or factual lookups
- File search, grep, directory listing
- Quick text formatting or transformations
- Generating short boilerplate code
- Answering single-step, well-defined questions
- Summarizing short content (< 500 tokens)
- Log parsing or pattern matching

**Signals:** One step, no reasoning chain required, low stakes, high frequency.

---

### 🟡 Standard — delegate to `p4-core:p4-standard` (Sonnet)
**Use when the task involves:**
- General software development tasks
- Implementing features or fixing bugs
- Code review and refactoring
- Writing tests for existing code
- PR review and description generation
- Multi-file edits with clear scope
- Moderate debugging (known error class)
- Writing documentation or READMEs
- Explaining or analyzing code

**Signals:** Moderate reasoning, 2–5 step execution, standard engineering work.

---

### 🔴 Advanced — delegate to `p4-core:p4-advanced` (Opus)
**Use when the task involves:**
- System or architecture design decisions
- Complex debugging with unknown root cause
- Security analysis and threat modeling
- Evaluating trade-offs between multiple approaches
- Generating or reviewing critical business logic
- Migrating large codebases or breaking changes
- Tasks where errors have high impact or are hard to reverse
- Cross-cutting concerns affecting multiple systems
- Performance optimization requiring deep profiling

**Signals:** Multi-step reasoning required, high stakes, ambiguity present, architectural impact.

---

## How to Apply This Skill

1. **Evaluate the task** using the matrix above — scope, stakes, reasoning depth, frequency
2. **Select the tier** — default to Standard when complexity is unclear
3. **Delegate** using the **Agent tool** (NOT a slash command / Skill tool) with the corresponding `subagent_type` and the complete task as `prompt`:

   | Tier | `subagent_type` |
   |------|----------------|
   | Simple | `p4-core:p4-lightweight` |
   | General | `p4-core:p4-standard` |
   | Complex | `p4-core:p4-advanced` |

   > ⚠️ These are **agent types**, not skills. Invoking them as `/p4-core:p4-advanced` will fail with "Unknown skill". Always use the `Agent` tool.

4. **Briefly explain** the routing decision to the user when relevant:
   > "Routing to p4-advanced (Opus) — this is an architectural decision with broad impact."
   > "Routing to p4-lightweight (Haiku) — quick file search, no reasoning needed."

## Important Rules

- **Never downgrade critical tasks** to save cost — correctness comes first.
- **Prefer p4-lightweight for agentic loops** where the same operation repeats many times.
- If the user has explicitly set a model preference in this session, respect it — do not override.
- If invoked with $ARGUMENTS, treat the argument as the task description for routing purposes.
