---
name: consensus-python-coding
description: >-
  Writes and refactors Python and Cython code to satisfy pganssle, wan, and
  pablogsal, defaulting to pganssle on style conflicts. Covers Python 3.13+
  idioms, static type hints, frozen dataclasses, Enum/StrEnum, collections.abc,
  module-level imports, stdlib utilities, scope discipline, and control-flow
  hygiene. Use whenever writing, editing, or scaffolding .py or .pyx files.
---

# Consensus Python Coding (`pganssle` + `wan` + `pablogsal`)

Write Python code that passes review by Paul Ganssle (`pganssle`), Zhanyong Wan (`wan`), and Pablo Galindo-Salgado (`pablogsal`). Assume **Python 3.13+** unless `pyproject.toml` or repository config specifies an older minimum version.

## 0. Scope Discipline

- **Never mix unrelated changes**: Do not touch unrelated lines for formatting or typing upgrades inside a bug-fix or feature PR.
- **Whole-file upgrades get their own PR**: If you are modernizing type syntax or reformatting an existing file, do the entire file at once in a separate dedicated PR.

## 1. Immutability & Data Modeling

Default every data carrier and collection to immutable types unless in-place mutation is part of its design.

| Need | Preferred Construct | Avoid |
| :--- | :--- | :--- |
| Value object / structured record | `@dataclasses.dataclass(frozen=True)` (or `@attrs.frozen` if `attrs` is already used) | `dict[str, Any]` with fixed keys, `NamedTuple`, mutable `@dataclass` |
| Closed set of modes / states | `class State(enum.Enum):` (or `enum.IntEnum`) | Boolean mode flags (`is_summary: bool = False`), magic strings |
| Closed set represented as strings at boundaries (CLI flags, JSON, wire formats) | `class Mode(enum.StrEnum):` (3.11+) | `tuple[str, ...]`, `class Mode(str, enum.Enum):` |
| Fixed sequence / module constant | `tuple[T, ...]` with `: Final[...]` | `list[T]` at module scope |
| Fixed membership table | `frozenset[T]` with `: Final[...]` | `set[T]` at module scope, linear `in` scans on large `tuple` |

- **Never use `NamedTuple` for domain records**: It leaks tuple indexing, unpacking, and length comparisons into your public API. Use `@dataclasses.dataclass(frozen=True, slots=True)` instead.
- **No unnecessary third-party model libraries**: Do not add `attrs` or `pydantic` to a stdlib-only project when `@dataclasses.dataclass(frozen=True)` suffices. If `attrs` is already in `pyproject.toml`, `@attrs.frozen` is idiomatic.

## 2. Type Hints & Signatures

Annotate every function, method, `@property` getter, test helper, script entrypoint, and module-level constant (`: Final[...]`), unless local project policy (for example, CPython `Lib/`) forbids type hints.

### Built-in Generics & Unions
- Write `list[str]`, `dict[str, int]`, `X | None`, and `X | Y` in all new files and modified signatures (Python 3.10+).
- Never write `Optional[X]`, `Union[X, Y]`, `List[X]`, or `Dict[K, V]` in new code.
- Use PEP 695 syntax (Python 3.12+) for type aliases and generics:
  ```python
  type JsonValue = str | int | float | bool | None | Sequence[JsonValue] | Mapping[str, JsonValue]

  def first_or_default[T](items: Sequence[T], default: T) -> T:
      return items[0] if items else default
  ```

### Abstract Containers at Boundaries (`collections.abc`)
- Accept abstract types in parameters (`Sequence[T]`, `Set[T]`, `Mapping[K, V]`, `Iterable[T]`, `Callable[[A], R]`) rather than forcing callers to construct a `list`, `set`, or `dict`.
- Return abstract read-only views from `@property` getters (`Sequence[T]`, `Set[T]`, `Mapping[K, V]`) when callers must not mutate internal state.
- Choose `Set[T]` over `Sequence[T]` whenever elements are unique or membership / intersection checks occur (`bool(allowed & observed)` runs at C speed in CPython).

### Make Invalid States Unrepresentable
- **Union of Products over Product of Unions**:
  - Good: `location: tuple[int, int] | None`
  - Bad: `line: int | None, column: int | None` (where both must be set or both `None`)
- **Coupled types across arguments/returns**: Use constrained type parameters (`def add[T: (int, str)](a: T, b: T) -> T:`) or `@typing.overload` instead of returning a wide union (`int | str`) that forces callers to cast.
- **Structural interfaces over string switches**: Accept a `typing.Protocol` strategy object instead of `backend: str = "default"`.
- **Named constructors over union `__init__`**: Keep `__init__` taking canonical fields; add `@classmethod` constructors (`from_path`, `from_bytes`, `from_dict`) for alternative inputs.
- **Parameterize every container**: Never write bare `dict`, `list`, `tuple`, `Callable`, or `Generator`.

## 3. Imports & Module Organization

- **Import modules, not individual functions or classes** (`pganssle` default):
  ```python
  from collections.abc import Mapping, Sequence, Set
  import contextlib
  import dataclasses
  import enum
  from pathlib import Path
  from typing import Final, Protocol, Self, overload

  from . import config
  ```
- **Exceptions**: Names from `collections.abc`, `typing`, and `pathlib.Path` may be imported directly.
- **Top-of-file placement**: Place all imports at the top of the module. Only defer an import inside a function to break a real circular dependency or avoid an expensive optional runtime dependency; add a short comment explaining why.
- **No alias clutter**: Never write `Request = results.Request` at module level just to shorten references.
- **Side-effect-free availability checks**: Use `importlib.util.find_spec("pkg") is not None` instead of `try: import pkg` when checking whether an optional dependency is installed.

## 4. Standard Library Idioms

- **Paths**: Accept `str | os.PathLike[str]` on public functions and immediately convert via `path = Path(raw_path)`. Never manipulate paths with `os.path.join` or string slicing.
- **Package resources & version**: Read bundled data via `importlib.resources.files(__package__)` and package versions via `importlib.metadata.version("pkg")` — never compute paths from `__file__`.
- **Lazy singletons & properties**: Use `@functools.cache` on zero-argument helper functions and `@functools.cached_property` on immutable classes. Never use mutable `global _CACHE` variables.
- **File I/O**: Use `Path.read_text(encoding="utf-8")` or `with open(path, encoding="utf-8") as f:`. Do not build custom chunked readers or `mmap` wrappers unless profiling demonstrates a bottleneck.
- **Clocks & deadlines**: Use `time.monotonic()` for elapsed time, polling loops, and timeouts (`deadline = time.monotonic() + timeout_s`). Use `datetime.datetime.now(datetime.UTC)` for wall-clock timestamps.
- **Multi-line text & regexes**: Build multi-line blocks with `textwrap.dedent` and `"\n\n".join(parts)`. Compile complex regexes once at module level with `re.VERBOSE` and a comment giving example matches.
- **Safe iteration**: Always pass `strict=True` to `zip(a, b, strict=True)` when iterables must have matching lengths.

## 5. Control Flow, State & Algorithmic Traps

- **Flat guard clauses**: Check negative/invalid conditions first and `return` or `raise` immediately. Do not nest the main logic inside deep `if/else` ladders.
- **Tight variable scope**: Define local variables right above their first use, not in a block at the top of the function.
- **Explicit exception suppression**: Never write `try: ... except SomeError: pass`. When ignoring a specific, expected error is genuinely right, write `with contextlib.suppress(SomeError):`.
- **DAG / graph walks require a global visited set**: When walking a dependency graph, AST, or cause chain for reachability or deduplication, keep a single `visited: set[int]` across the entire traversal. Passing a per-path copy (`seen | {node}`) causes exponential blowup on diamond fan-out.
- **Reset state on reusable objects**: If a parser, analyzer, or runner class can be called more than once, clear per-call buffers and state at the start of its entrypoint method so state never leaks across calls.

## 6. Standalone Scripts (`uv` PEP 723)

When creating a standalone executable script that uses third-party libraries, include PEP 723 inline metadata at the top so `uv run script.py` manages its environment automatically:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "rich>=13.0",
# ]
# ///
```

## Quick Checklist Before Finishing `.py` Files
- [ ] Untouched lines in existing files are left unmodified (no mixed-concern formatting or typing churn).
- [ ] Frozen dataclasses (`@dataclasses.dataclass(frozen=True)`) and `Enum`/`StrEnum` replace loose dicts, `NamedTuple` records, and boolean mode flags.
- [ ] Every function, method, `@property`, and `: Final[...]` constant has complete Python 3.10+ type hints (`X | None`, `Sequence`, `Set`, `Mapping`), unless project policy forbids them.
- [ ] Imports are module-level at the top of the file (only `collections.abc`, `typing`, and `Path` imported directly).
- [ ] Preconditions use early guard clauses; `zip(..., strict=True)`, `time.monotonic()`, and `Path` are used throughout.
- [ ] Graph walkers use a global `visited` set; reusable stateful classes reset per-call state on entry.
