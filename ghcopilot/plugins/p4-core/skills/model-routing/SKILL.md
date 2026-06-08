---
name: model-routing
description: This skill should be used when Copilot needs to decide which model to use for a task, when handling requests that vary significantly in complexity, or when optimizing cost vs. quality trade-offs. Activates automatically when Copilot detects task complexity signals that suggest a different model would be more appropriate.
---

# Model Routing — Intelligent Task-Based Model Selection

This skill guides Copilot in automatically selecting the most appropriate model based on task complexity and nature, balancing quality, speed, and cost.

## Routing Decision Matrix

### 🟢 Lightweight Model — Fast & Cheap
**Use when the task involves:**
- Simple questions or factual lookups
- File search, grep, directory listing
- Quick text formatting or transformations
- Generating short boilerplate code
- Answering single-step, well-defined questions
- Summarizing short content (< 500 tokens)
- Log parsing or pattern matching

**Signals:** Task can be answered in one step, no reasoning chain required, low stakes, high frequency.

---

### 🟡 Standard Model — Balanced & General-Purpose *(default)*
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

**Signals:** Task requires moderate reasoning, 2–5 step execution, standard engineering work.

---

### 🔴 Advanced Model — Deep Reasoning & Critical Work
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

When starting a task, evaluate:

1. **Scope**: Is this one step or many?
2. **Stakes**: What's the cost of a mistake?
3. **Reasoning depth**: Does this need chain-of-thought or inference?
4. **Frequency**: Is this a repeated lightweight task?

Then select accordingly and, when relevant, explain the routing choice:

> "This is an architectural decision with broad impact — using the advanced model for deeper analysis."
> "This is a quick file search — lightweight model is the right fit here."

## Rules

- **Default to the standard model** when the complexity is unclear.
- **Never downgrade critical tasks** to save cost — correctness comes first.
- **Prefer lightweight models for agentic loops** where the same operation repeats many times.
- If the user has explicitly set a model preference in this session, respect it and do not override.
