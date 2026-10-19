---
name: consensus-coding
description: >-
  Writes, refactors, and tests code to satisfy the combined standards of Paul
  Ganssle (pganssle), Zhanyong Wan (wan), and Pablo Galindo-Salgado (pablogsal),
  defaulting to pganssle when they disagree. Acts as the top-level umbrella and
  router across five domain sub-skills (consensus-python-coding,
  consensus-api-design, consensus-testing, consensus-cpp-and-native,
  consensus-build-and-ci). Use whenever writing, editing, refactoring, or
  scaffolding Python, C/C++ extensions, ML compiler/runtime code, tests, or
  build/CI configurations.
---

# Consensus Coding Skill Suite (`pganssle` + `wan` + `pablogsal`)

Write, refactor, and test code that passes review by Paul Ganssle (`pganssle`), Zhanyong Wan (`wan`), and Pablo Galindo-Salgado (`pablogsal`) on the first pass. Where the three reviewers agree, apply the union of their technical standards. Where they disagree, default to `pganssle`'s preference unless the local project's explicit policy says otherwise.

## Domain Sub-Skills Routing Table

Load only the sub-skills matching the files you are writing or editing. For multi-domain changes, load each relevant sub-skill before writing code.

| Domain | Sub-Skill | When to Load |
| :--- | :--- | :--- |
| **Python Code & Types** | [`consensus-python-coding`](./consensus-python-coding/SKILL.md) | Writing or refactoring `.py` / `.pyx` code: Python 3.13+ idioms, type hints, `@dataclass(frozen=True)`, `Enum` / `StrEnum`, `collections.abc`, module-level imports, control flow, stdlib helpers. |
| **APIs, Naming & Errors** | [`consensus-api-design`](./consensus-api-design/SKILL.md) | Designing modules, public/private boundaries, identifier names, CLI flags, config files, exceptions, warnings, or docstrings. |
| **Tests & Test Doubles** | [`consensus-testing`](./consensus-testing/SKILL.md) | Writing or updating tests (`pytest`, `hypothesis`, `unittest`, `GoogleTest`, `gMock`, `FuzzTest`), fixtures, fakes, or mocks. |
| **C, C++ & ML Native Code** | [`consensus-cpp-and-native`](./consensus-cpp-and-native/SKILL.md) | Writing CPython C extensions (PEP 7, refcounts, GC), Rust-style `const`-by-default C++, or Google/Abseil/TorchTPU C++. |
| **Build, CI, Docs & VCS** | [`consensus-build-and-ci`](./consensus-build-and-ci/SKILL.md) | Editing `BUILD`/`.bzl`, `pyproject.toml` (`flit`/`tox`/`nox`/`uv`/modern native backends), GitHub Actions, changelogs/NEWS, `README.md`, or commit messages. |
| **Reviewer Differences** | [references/reviewer-disagreements.md](references/reviewer-disagreements.md) | Checking genuine preference differences vs. ecosystem artifacts among `pganssle`, `wan`, and `pablogsal`. |

---

## Core Engineering Principles

1. **The Best API Is No API (Hyrum's Law)**: Every public symbol, parameter, and config knob is a permanent maintenance burden. Default all new modules, helpers, attributes, and constants to private (`_` prefix); expose public APIs only deliberately. Reuse standard library and upstream ecosystem primitives over bespoke wrappers.
2. **Scope Discipline (One Concern Per PR)**: Never mix unrelated formatting, typing upgrades, or cleanups into a functional PR. Do not churn untouched lines; if a whole file needs modernization, do that file all at once in a separate dedicated PR.
3. **Make Invalid States Unrepresentable**: Use frozen dataclasses, `Enum` (or `StrEnum` when string representation is needed at boundaries), `Literal`, `collections.abc` abstract containers (`Sequence`, `Set`, `Mapping`), PEP 695 `type X = ...` aliases, and Union-of-Products signatures (`tuple[int, str] | None`, constrained `[T: (int, str)]`, or `@overload`) instead of loose dicts, `NamedTuple` records, magic strings, or Product-of-Unions types.
4. **Self-Evident, Positive, Faithful Naming**: Names must state semantic role and exact behavior (`_GPU_GOLDEN_PLATFORM`, not `_GPU_B200_PLATFORM`; `has_surrounding_whitespaces`, not `no_surrounding_whitespace`; `--test-all`, not `--disable-bazel-diff`). If a function's name promises X and its body also does Y, rename or split it.
5. **Hard Separation Between Programmer Bugs and User Errors**:
   - **Internal invariant violations (programmer mistakes)** crash immediately (`assert`, `ABSL_CHECK`, `TT_CHECK`, `TORCH_INTERNAL_ASSERT`).
   - **User-triggerable input errors** raise narrow, spec-compliant exceptions (`ValueError` for bad values, `TypeError` for unsupported types/operations, `NotImplementedError` only for abstract or unfinished implementations) using `expected <requirement>, got <actual>` phrasing, after validating the full input before mutating state.
6. **Fail Loudly — Never Swallow Errors**: Never return `None`/`False` as an error sentinel or catch broad `except Exception:` / `except OSError:` / `except SyntaxError: pass` to hide failures. Let exceptions propagate; when a narrow, expected error is intentionally ignored, use `with contextlib.suppress(SpecificError):`.
7. **Tests Must Falsify Bugs, Not Lock In Implementation**:
   - Follow `Real > Fake > Stub > Mock`. Test the public contract only; aim for 100% coverage and hunt for edge cases.
   - Every test must pass the **Counterfactual & Mutation Check**: if you mentally delete or invert the production branch, constraint, or state update under test, the test must fail.

---

## Default Choices Across Reviewer Preferences & Ecosystems

When `pganssle`, `wan`, and `pablogsal` differ (or work in different default ecosystems), apply these defaults unless overridden by local project policy:
- **Target Python**: Assume **Python 3.13+** unless `pyproject.toml` or repo config specifies an older floor.
- **Unions & Optionals**: Write `X | None` and `X | Y` in new code and modified signatures (3.10+); leave untouched lines alone.
- **Imports**: Import modules (`from . import results` -> `results.Request`; `import attrs` -> `attrs.frozen`), never individual functions or classes. Only `collections.abc` containers, `typing` constructs (`Final`, `Protocol`, `overload`, `Self`, `TypeVar`), and `Path` may be imported directly.
- **Type Hints**: Annotate all functions, methods, `@property` getters, scripts, constants (`Final[...]`), and test helpers, unless local project policy (such as CPython `Lib/`) forbids annotations.
- **Enums**: Use `enum.Enum` by default; use `enum.StrEnum` (3.11+) when enum values must cross a string communication layer (CLI flags, serialization, env vars). Never write `class Foo(str, Enum):` in 3.11+.
- **Test Stack**: Default to `pytest`, `hypothesis`, fixtures (never inheritance/mixins), `@pytest.mark.parametrize`, and `tox`. Test only the public contract; always pass `autospec=True` whenever a mock is unavoidable.
- **Packaging**: Default to `flit` (`flit_core.buildapi`) for pure-Python packages; avoid `setup.py` whenever possible. For compiled C/C++ extensions, choose a modern backend (`meson-python`, `hatch`, `scikit-build-core`, or `bazel`) on a case-by-case basis. Use `# /// script` (`uv` PEP 723 metadata) for standalone scripts with dependencies.
- **Config Modularity**: Pull repository-specific paths, layout maps, exclusion regexes, and size limits into a root configuration file rather than hardcoding them inside reusable tool modules.
- **C++ `const` Discipline**: Write C++ like Rust — mark every local variable, parameter, and method `const` unless mutation or `std::move` is required, unless overridden by local project style (such as Abseil Tip #109 in `.h` declarations).
- **GitHub Actions**: Pin third-party actions to full 40-character commit SHAs with a `# vX.Y.Z` comment (`zizmor` standard), and configure automated SHA updates (Dependabot / Renovate) or leave a `TODO` to set up automated updates.

---

## Pre-Finish Self-Audit Checklist

Before considering any code change complete, check every modified file top-to-bottom:
1. **No dead code, stale references, or scope creep**: Untouched lines are left alone; every added variable, helper, parameter, and constant is used; every deleted symbol, flag, tool, or config key has zero lingering references across code, build files, CI, docs, and tests.
2. **Exact types & immutability**: All signatures use `Sequence` / `Set` / `Mapping` where mutation is not needed; constants carry `: Final[...]` and use `tuple` or `frozenset`; C++ locals/methods are `const` by default; no `dict` with fixed keys or `NamedTuple` domain records remain.
3. **Boundary & error hygiene**: Inputs are normalized once at the producer boundary; preconditions are asserted or validated before side effects; error messages state `expected ..., got ...` (or accepted syntax) without internal variable names.
4. **Clarity layer**: Docstrings use third-person declarative verbs (`Returns...`, `Sets...`); comments explain *why* and non-local invariants (never repeating the code); magic limits link to their source of truth; complex regexes use `re.VERBOSE`.
5. **Test falsification**: Every new branch, error raise, and `except ImportError:` fallback has a test that fails when the code under test is broken.
