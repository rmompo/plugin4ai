---
name: typescript-standards
description: Activates TypeScript/JavaScript-specific coding standards for the session, complementing the universal P4C directives. Invoke manually or when package.json / tsconfig.json is detected. Also invoked explicitly as /p4-coding:typescript-standards.
version: 2
argument-hint: ""
allowed-tools: [Bash]
---

# P4C-TS — TypeScript / JavaScript Standards

These directives complement the universal standards (P4C-001 to P4C-016) and apply specifically to TypeScript and JavaScript projects.

---

## P4C-TS-001 — Strict mode is mandatory

Enable `"strict": true` in `tsconfig.json`. Never use `any` — prefer `unknown` with explicit narrowing. The only acceptable `any` is at system/library boundaries where types are genuinely unavailable, and it must be justified with a comment.

---

## P4C-TS-002 — Explicit types at boundaries

Explicitly type parameters and return values of all public/exported functions. Allow inference only for internal variables where the type is immediately obvious. API contracts must always be explicit.

---

## P4C-TS-003 — Async/Await over raw Promises

Prefer `async/await` over chained `.then()/.catch()`. Always handle the rejection case — never leave Promises unawaited in async contexts. Use `Promise.all()` / `Promise.allSettled()` for parallel execution.

---

## P4C-TS-004 — Null safety

Never use the non-null assertion operator (`!`) without an explicit comment justifying it. Prefer optional chaining (`?.`) and nullish coalescing (`??`). Make nullability explicit in types (`string | null`, not just `string`).

---

## P4C-TS-005 — Immutability

Prefer `const` over `let`. Never use `var`. Use `readonly` on properties that must not mutate. Prefer `Readonly<T>` and `ReadonlyArray<T>` for function parameters that must not be mutated.

---

## P4C-TS-006 — Modules

Prefer ESM (`import`/`export`) over CommonJS (`require`). One primary export per file as a general rule — exceptions must be intentional and documented. Avoid barrel re-exports that create circular dependency risk.

---

## P4C-TS-007 — Typed error handling

Use custom error classes that extend `Error`. Set `name` explicitly to the class name for reliable `instanceof` checks. In TypeScript 5+, use `satisfies` to validate error structures. Never `throw` strings or plain objects.

---

## P4C-TS-008 — Avoid problematic patterns

- Always use `===`, never `==`.
- Never use `eval()` or `new Function()` with strings.
- Never mutate function parameters directly — clone first if modification is needed.
- Never use `delete` on object properties — prefer destructuring with omission.
- Never use `Object.assign` with a non-empty target for immutable operations — spread instead.

---

## P4C-TS-009 — Testing (Jest / Vitest)

- Test files live next to source files (`*.spec.ts` or `*.test.ts`).
- Mock at the module boundary, not internally.
- Do not use `expect.assertions(N)` without a documented reason.
- Prefer `vi.fn()` / `jest.fn()` over real implementations in unit tests.
- Test file names must mirror their source file: `user.service.spec.ts` for `user.service.ts`.

---

## P4C-TS-010 — Linting and formatting

ESLint + Prettier are mandatory. Configuration must be committed to the repo and shared across the team. Minimum required rules: `@typescript-eslint/no-explicit-any`, `no-unused-vars`, `prefer-const`. CI must enforce lint — no warnings allowed in production branches.
