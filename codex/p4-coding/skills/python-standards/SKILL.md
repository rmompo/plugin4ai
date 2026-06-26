---
name: python-standards
description: Activates Python-specific coding standards for the session, complementing the universal P4C directives. Invoke manually or when pyproject.toml / requirements.txt is detected. Also invoked explicitly as /p4-coding:python-standards.
---

# P4C-PY — Python Standards

These directives complement the universal standards (P4C-001 to P4C-016) and apply specifically to Python projects.

---

## P4C-PY-001 — PEP 8 compliance

Follow PEP 8 strictly. Use `ruff` (preferred) or `flake8` + `black` for automatic enforcement. Maximum line length: 88 characters (black default). Format on save is mandatory.

---

## P4C-PY-002 — Type hints are mandatory

Annotate all parameters and return values of public functions. Use `from __future__ import annotations` for forward references. Configure `mypy` in strict mode (`--strict`). Do not use `Any` from `typing` without a documented justification.

---

## P4C-PY-003 — Context managers for resources

Always use `with` for resources that must be closed (files, connections, locks, database sessions). Never rely on manual `.close()` calls — they are not guaranteed to execute. Implement `__enter__`/`__exit__` or use `contextlib.contextmanager` for custom resource managers.

---

## P4C-PY-004 — Exception handling

- Never use bare `except:` or `except Exception:` without re-raising or explicit logging with context.
- Create a custom exception hierarchy derived from `Exception` for domain errors.
- Use `raise ... from err` to preserve the original stack trace when wrapping exceptions.
- Catch the most specific exception type possible.

---

## P4C-PY-005 — Dataclasses and Protocols

- Prefer `@dataclass` or `@dataclass(frozen=True)` over classes with only `__init__`.
- Use `Protocol` (PEP 544) for structural duck typing instead of ABCs where possible — it avoids inheritance coupling.
- Use `TypedDict` for dictionaries with known structure. Never pass untyped `dict` at system boundaries.

---

## P4C-PY-006 — Immutability and state

- Prefer `tuple` over `list` for collections that must not mutate.
- Never use mutable objects as default parameter values (`def f(x=[])` is a classic bug).
- Prefer pure functions; isolate side effects to specific layers (repositories, services).

---

## P4C-PY-007 — Generators and iterators

Prefer generators over lists when iterating only once — they save memory and are lazily evaluated. Use `itertools` for iterator composition before implementing manually. Use `yield from` for generator delegation.

---

## P4C-PY-008 — Imports

- Import order: stdlib → third-party → local (enforced by `isort` or `ruff`).
- No implicit relative imports. Explicit relative imports (`from . import X`) are acceptable; `from package import X` at module level is preferred.
- Never use `import *` — always be explicit about what is imported.

---

## P4C-PY-009 — Testing (pytest)

- Use `pytest` + `pytest-cov`. Do not use `unittest` unless inheriting legacy code.
- Place shared fixtures in `conftest.py` for appropriate scope (function/class/module/session).
- Use `@pytest.mark.parametrize` instead of loops inside test functions.
- Use `unittest.mock` or `pytest-mock` for mocking. Mock at the boundary, not internally.
- Test coverage minimum: 80% for new code in production modules.

---

## P4C-PY-010 — Environments and dependencies

- Always declare dependencies in `pyproject.toml` (PEP 517/518). Avoid `setup.py` for new projects.
- Separate development dependencies from production ones (`[project.optional-dependencies]` or `[tool.poetry.dev-dependencies]`).
- Pin exact versions in production deployments (`==`), use ranges in libraries (`>=x.y,<x+1`).
- Never commit virtual environments or `.pyc` files to version control.
