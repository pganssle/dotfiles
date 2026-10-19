---
name: consensus-api-design
description: >-
  Designs module boundaries, public APIs, identifier names, config files,
  exceptions, warnings, and docstrings to satisfy pganssle, wan, and pablogsal.
  Covers Hyrum's Law, config-driven modularity, positive role-based naming,
  boundary normalization, all-or-nothing validation, and canonical error
  messages. Use whenever designing functions, classes, CLIs, error contracts,
  or documentation.
---

# Consensus API Design, Naming & Error Contracts (`pganssle` + `wan` + `pablogsal`)

Design interfaces that are minimal, hard to misuse, and honest about what they do. Every public symbol is a long-term commitment; every error message is part of the user interface.

## 1. Hyrum's Law & Public Surface Discipline

- **Default everything to private (`_`)**: Prefix internal modules (`_parser.py`), internal subpackages (`_internal/`), helper functions (`_build_index()`), class attributes (`self._cache`), and module constants (`_DEFAULT_TIMEOUT_S`) with `_`.
- **Keep `__init__.py` minimal**: Re-export only the deliberate user-facing surface. Do not dump internal submodules into `__all__`.
- **Never use `Public*` prefixes**: Public classes get clean domain names (`Client`, `Session`); internal implementations get leading underscores (`_ClientState`).
- **Separate public and internal environment variables**: Public env vars use the clean project prefix (`TORCH_TPU_...`, `MYPKG_...`); internal debug/testing knobs use `..._INTERNAL_...` so users do not depend on unstable toggles.
- **No Attractive Nuisances**: Never ship a convenience API that looks safe and general but silently drops records, truncates results, or degrades to $O(N^2)$ on realistic inputs. Either make it safe or keep it private with explicit preconditions.

## 2. Config-Driven Tool Modularity

- **Separate generic engines from repository policy** (`pganssle` default): Keep linters, build scripts, analyzers, and CLI engines free of hardcoded project paths, directory layout maps, exclusion regexes, and file-size caps.
- **Root configuration file**: Load repository-specific paths, exclusions, and thresholds from a root config file (`pyproject.toml` `[tool.xyz]` or a dedicated config file) passed into a frozen config dataclass at startup.
- **Module-level constants**: Reserve `_`-prefixed `: Final[...]` module constants for genuine algorithmic, protocol, or ABI invariants.

## 3. Naming Precision

Names must describe semantic role and exact behavior without leaking current literal values or return types.

| Anti-Pattern | Preferred Name | Why |
| :--- | :--- | :--- |
| `_GPU_B200_PLATFORM` | `_GPU_GOLDEN_PLATFORM` | Names the semantic role, not today's literal hardware SKU. |
| `no_surrounding_whitespace` / `--disable-diff` | `has_surrounding_whitespaces` / `--test-all` | Positive predicates avoid double negatives (`if not no_...:`). |
| `out_dtype` | `result_dtype` | Clearer role; avoids confusion with `out=` buffer parameters. |
| `get_user_list()` | `get_users()` | Do not encode concrete container types in function names. |
| `serialize_to_proto()` (in-memory) | `convert_to_proto()` / `ToProto()` | `Serialize` means converting to bytes/wire format; `Convert` transforms in-memory structures. |
| `"stacktrace"` (for status hops) | `"status propagation trace"` | Stack traces record call frames; status traces record error-return hops. |
| `items_as_sets` (when duplicates exist) | `items_as_multiset` / `item_counts` | Never say `set` when multiplicity is preserved. |
| `shape_compatibility()` (raises on bad shape) | `check_shape_compatibility()` / `validate_shape()` | Helpers that raise on invalid state must start with an imperative verb. |

- **Name-vs-body fidelity**: If a function is named `find_config()` or `is_valid()`, it must not mutate state, write files, or spawn processes. If it does both, split the query from the modifier or rename it (`load_and_cache_config()`).

## 4. Boundary Normalization & Preconditions

- **Normalize once at the producer boundary**: Convert raw strings to `Path`, `Enum` / `StrEnum`, or frozen dataclasses at the CLI, config-loader, or public entrypoint boundary. Internal helpers should accept already-typed objects and never repeat defensive `.strip()` / `Path(x)` conversions.
- **No silent `.lower()` on enum inputs**: Parse `Mode(raw_value)` directly and let invalid casing fail loudly unless case-insensitive input is an explicit documented requirement.
- **All-or-nothing validation**: Validate every input argument and precondition *before* mutating `self`, writing to disk, or updating external state. A failed call must leave the system untouched.
- **Assert internal invariants**: Use `assert` (or `ABSL_CHECK` / `TT_CHECK` in C++) for conditions guaranteed by your own callers (`assert workspace_dir.is_dir()`).

## 5. Error Semantics & Exception Hierarchy

Follow Python's documented built-in exception semantics (`Doc/library/exceptions.rst`):

- **Internal bug** (broken invariant inside our own code): `assert`, `ABSL_CHECK`, `TT_CHECK`.
- **Bad caller argument value** (right type, out-of-range or invalid value): `ValueError`.
- **Wrong argument type or operation unsupported by design on this object**: `TypeError` (or a custom project exception subclass).
- **Abstract base method or feature planned but not yet implemented**: `NotImplementedError`. Never raise `NotImplementedError` for invalid argument values or for operations that are never meant to be supported on a type/mode.
- **Canonical error message format**:
  - Write `expected <requirement>, got <actual!r>` (for example, `f"expected positive batch_size, got {batch_size}"`).
  - Never expose internal parameter names (`lhs`, `rhs`, `self._buf`) when user-facing concepts (`first tensor`, `input path`) exist.
  - On parser, config, or DSL errors, state what syntax *is* valid instead of bare `"invalid syntax"`.
  - Do not wrap messages in redundant prefixes (`"Error: failed to parse: error: ..."`).
- **Custom exception classes (`errors.py`)**:
  - Group project-specific exceptions under a common base (`class MyProjectError(Exception):`) in `errors.py`.
  - Never call `sys.exit()` or `raise sys.exit(1)` inside library functions; raise a domain exception and translate it to `stderr` + exit code only in `__main__.py` / `main()`.
  - Keep `try:` blocks tight — wrap only the single call that can raise, putting follow-up work in `else:`.

## 6. Warnings & Diagnostics

- **Custom warning class**: Subclass `UserWarning` (`class MyProjectWarning(UserWarning):`) so callers can filter your library's warnings cleanly.
- **Use stdlib warning filters**: Call `warnings.warn("...", MyProjectWarning, stacklevel=2)` and rely on Python's warning registry (`"once"` / `"default"`) rather than module-level `global _WARNED` flags.
- **No import-time noise**: Importing a package on a standard environment must never emit warnings or print to stdout/stderr.
- **Actionable diagnostics**: Never suggest environment changes that cannot work at runtime (such as setting `LD_PRELOAD` after the process has already started).

## 7. Docstrings & Comments

- **Third-person declarative verbs**: Begin every docstring summary with a third-person verb (`Returns the normalized path.`, `Sets the active device.`, `Converts an AST node to...`), never imperative (`Return...`, `Set...`).
- **Explain *why*, never *what***: Delete comments that restate the code (`# increment i`). Keep comments that explain *why* an alternative was rejected, cite external specs/issues on `# type: ignore[code]`, document magic ABI/register constants, or warn about non-local invariants.
- **Complex regexes**: Always write multi-part regular expressions with `re.VERBOSE` and include a comment showing 1–2 concrete example strings that match.

## Quick Checklist Before Finishing APIs & Errors
- [ ] Every internal module, helper, attribute, and constant starts with `_`; `__init__.py` exports only the public contract.
- [ ] Repo-specific paths, exclusions, and limits live in a root config file, not hardcoded inside generic tools.
- [ ] Booleans and CLI flags are positive; names reflect semantic role (`_GOLDEN_PLATFORM`) and match function behavior.
- [ ] Inputs are normalized once at the boundary and validated completely before any state mutation.
- [ ] Exceptions follow Python's spec (`ValueError` for bad values, `TypeError` for unsupported operations, `NotImplementedError` only for abstract/unfinished code); docstrings start with `Returns...` / `Sets...`.
