---
name: model-route
description: Evaluates task complexity and selects the appropriate processing tier (lightweight / standard / advanced) as a behavioral hint. Activates automatically when task complexity signals are detected. Also invoked explicitly as /p4-core:model-route with an optional task description.
version: 30
argument-hint: "[task description]"
allowed-tools: [Bash]
---

# Model Routing — Task Tier Reference

This skill evaluates the current task and determines the appropriate processing tier, expressed as a behavioral hint for the AI assistant.

## Routing Decision Matrix

### 🟢 Lightweight — simple, fast tasks
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

### 🟡 Standard — general engineering work
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

### 🔴 Advanced — high-stakes, complex reasoning
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
3. **Apply the tier as context**: this CLI does not support subagent delegation — use the selected tier to calibrate your response depth, thoroughness, and validation rigor:
   - 🟢 Lightweight → fast, direct, minimal explanation
   - 🟡 Standard → complete solution with clear reasoning
   - 🔴 Advanced → deep analysis, trade-offs documented, validation steps included
4. **Briefly note the routing decision** when relevant:
   > "Applying advanced-tier reasoning — architectural decision with broad impact."
   > "Applying lightweight tier — quick file lookup, no chain of thought needed."

## Important Rules

- **Never downgrade critical tasks** to save effort — correctness comes first.
- Default to Standard when complexity is unclear.
- If the user has explicitly set a model preference in this session, respect it — do not override.
- If invoked with $ARGUMENTS, treat the argument as the task description for routing purposes.
