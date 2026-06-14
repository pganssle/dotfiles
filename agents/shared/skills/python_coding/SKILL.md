---
name: python-coding
description: >
  Style and conventions for writing Python code the way the user wants it.
  Use this skill whenever you write, edit, refactor, or review Python code, or
  scaffold a Python script or library. It covers type hints, immutability,
  import style, modern Python idioms (3.12+), avoiding primitive obsession, and
  uv-style dependency comments for scripts. Apply it by default to any Python
  the user asks for unless they explicitly override a convention.
---

# Python coding style

Write Python that follows the conventions below. These are defaults: if the
user explicitly asks for something different, honor their request, but
otherwise apply all of these without being asked.

## Target version

- Write assuming **Python 3.13+**. Use modern syntax and standard-library
  features freely; do not add compatibility shims for older versions.

## Types and data

- **Prefer immutable types to mutable types** where possible (e.g. `tuple`
  over `list`, frozen `attrs` classes, `frozenset`) unless mutation is genuinely
  needed.
- **Always use static type hints.** When type hinting, prefer generic
  containers from `collections.abc` (e.g. `collections.abc.Sequence`,
  `collections.abc.Mapping`, `collections.abc.Iterable`) over concrete types
  like `list` or `dict` in signatures.
- **Never use `typing.List` or any pre-PEP 585 container types.** Use the
  built-in generics (`list[int]`, `dict[str, int]`) where a concrete type is
  appropriate.
- In modern Python you don't need `Union` — use `X | Y`. You don't need
  `Optional` — use `X | None`.
- **Avoid primitive obsession.** Use the right type for the domain: `pathlib.Path`
  instead of string paths, `datetime.datetime` instead of string or integer
  dates, `enum.Enum` instead of magic strings/ints, etc.

## Structure

- **Avoid global variables.**
- **Avoid recursion** unless an iterative version would make the code
  meaningfully messier.

## Imports

- Prefer **module-level import style**: `from . import results` and then
  reference `results.Request`, rather than `from .results import Request`.
- This also applies to third-party packages: `import attrs` and use
  `attrs.frozen`, rather than `from attrs import frozen`.
- **The only exception** is generic containers from `collections.abc` and
  typing-specific names like `typing.Final`, which may be imported directly.

## Scripts vs. libraries

- If asked for a **script** (rather than a library) and the script has any
  dependencies, declare them with a **uv-style dependency comment** at the top
  of the file:

  ```python
  # /// script
  # dependencies = [
  #   "attrs",
  #   "numpy>1.2",
  # ]
  # ///
  ```

For libraries,  use modern Python programming idioms to create packages. Prefer
flit as a build backend and Apache 2.0 as the license.  Do not use dynamic
versions and read the README.md as the long description.
