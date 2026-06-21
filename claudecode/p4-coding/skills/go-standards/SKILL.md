---
name: go-standards
description: Activates Go-specific coding standards for the session, complementing the universal P4C directives. Invoke manually or when go.mod is detected. Also invoked explicitly as /p4-coding:go-standards.
version: 4
argument-hint: ""
allowed-tools: [Bash]
status: proposal
---

# P4C-GO — Go Standards

> **Status: PROPOSAL — Content pending implementation.**
>
> This skill is scaffolded but not yet implemented. Planned directives will cover:
> - Go idioms: channels, goroutines, select
> - Error handling (no exceptions — always return `error`)
> - Interface segregation Go-style (implicit interfaces)
> - Package naming and structure conventions
> - `defer` usage patterns
> - Context propagation (`context.Context`)
> - Testing with `go test` and table-driven tests
> - Linting with `golangci-lint`
> - Dependency management with Go modules

---

## TODO: define skill steps here
