---
name: python-testing
description: >
  Conventions for writing Python tests the way the user wants them. Use this
  skill whenever you write, edit, or review Python tests, or when asked to add
  test coverage for a module. It covers pytest/hypothesis usage, testing only
  the public contract, parametrization, fixtures over inheritance, edge cases,
  and aiming for 100% coverage. Use it alongside the python-coding skill, which
  covers general Python style.
---

# Python testing style

Write tests following the conventions below. These are defaults: honor an
explicit request from the user that conflicts, but otherwise apply all of these
without being asked. For general Python style (types, imports, immutability,
etc.) also follow the **python-coding** skill — the points repeated here are the
ones that matter most for tests.

## Tooling

- Write assuming **Python 3.13+** unless otherwise a different support matrix is
  specified in the pyproject.toml.
- Assume the **latest `pytest` and `hypothesis`** are available, and use them,
  again unless the dependency declaration specifies a different minimum version:
  you may bump minimum versions to get new features for test dependencies in
  most cases.
- Use `tox` to orchestrate tests, linting, etc.

## What to test

- Treat the thing under test as a **contract about the module's public
  interface**. Test that public contract only — **do not test the private
  interface** (underscore-prefixed names, internal helpers, implementation
  details).
- Aim for **100% code coverage** of the module under test.
- **Hunt for edge cases** — boundaries, empty inputs, error paths, unusual but
  valid inputs — and cover as many as you can find.

## How to structure tests

- **Prefer parametrized tests** (`@pytest.mark.parametrize`) to repeated,
  copy-pasted test bodies.
- Use **fixtures** for modular, composable setup. Do **not** use mixins or class
  inheritance to share test setup.
- Use **`hypothesis`** (property-based testing) wherever it fits — e.g. when a
  property should hold across a wide input space rather than a few hand-picked
  examples. When writing or reviewing property tests, also use
  [python-property-testing](../python-property-testing/SKILL.md) for choosing
  properties, designing strategies, investigating failures, and keeping CI
  costs reasonable.

## Style

- Prefer immutable types to mutable types where possible.
- Avoid global variables and recursion unless avoiding them makes the code
  meaningfully messier.
- Always use static type hints; prefer generic containers from
  `collections.abc` (e.g. `collections.abc.Sequence`) over concrete types.
  Never use `typing.List` or other pre-PEP 585 container types; use `X | Y` and
  `X | None` instead of `Union`/`Optional`.
- Prefer module-level imports (`from . import results`, then `results.Request`).
  The only exception is generic containers from `collections.abc` and
  typing-specific names like `typing.Final`.
- Avoid primitive obsession — use `pathlib.Path` for paths,
  `datetime.datetime` for dates, etc.
