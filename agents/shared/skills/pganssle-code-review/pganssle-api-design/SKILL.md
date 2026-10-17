---
name: pganssle-api-design
description: >-
  Reviews and designs public API surfaces, config-driven tool modularity, module
  and __init__.py hygiene, stdlib idioms, CPython set intersection performance,
  caching (@functools.cache), and exception/warning semantics emulating Paul
  Ganssle (pganssle). Use when reviewing API boundaries, CLI/linter tool
  architecture, file I/O helpers, error handling, or Python idioms. Don't use for
  C++ kernel logic, CI/CD workflow YAML, or test mock setup (use
  pganssle-cpp-and-ml, pganssle-build-and-ci, or pganssle-testing-and-mocks).
---

# Paul Ganssle (`pganssle`) — API Surface Governance, Config-Driven Modularity & Error Semantics

Review and design API surfaces, modular tools, stdlib idioms, caching, and error semantics with the architectural discipline of Paul Ganssle (`pganssle`).

> **Completeness & Line-Anchoring Contract**:
> - **Never self-cap findings**: Audit every modified file top-to-bottom. Do not skip module aliases, hardcoded config constants, or file I/O helpers in a file just because you already found a logic bug in that file.
> - **Anchor separately at each declaration**: When multiple hardcoded constants, path maps, exclusion regexes, or byte limits appear in a file, emit a **separate, concise comment at each offending constant definition**.

---

## 1. Config-Driven Tooling & Separating Generic Engine from Repo Layout

### Pull Repository Layout, Exclusions & Size Thresholds into a Root Config File
When reviewing a CLI tool, linter, test runner, or infrastructure utility, check whether repository-specific constants or tunable policies are hardcoded at the top of the engine or parser modules:
1. **Repository & monorepo directory names** (e.g., hardcoded monorepo root directory names).
2. **Canonical path roots, rules paths, and layout rewrite maps** (e.g., mapping OSS directory paths back to monorepo canonical paths).
3. **Default path-exclusion regular expressions** (e.g., compiled regexes excluding specific tool directories, metadata files, or file extensions).
4. **File-size or buffer byte limits** (e.g., `1 << 20` byte caps for whole-file matching).

- **Why**: Hardcoding project-specific directory names, path maps, exclusion patterns, and byte limits inside the engine couples the tool to one repository and prevents open-sourcing or reusing it as a generic utility.
- **How to comment (anchor separately at each constant block)**:
  - At the monorepo directory constant: *"We don't have to optimize for this too much but if we're adding a config file this should go in there too. I was hoping we might open source this at some point and make it a generic utility."*
  - At the canonical root / path-mapping table: *"I would pull everything like this from a config file, preferably at repo root."*
  - At the default excluded-path regex: *"We should be able to override this in a config file."*
  - At the max file-size byte constant: *"I would make this configurable in the config file."*

---

## 2. API Surface Minimalism, `__init__.py` Hygiene, Module Aliases & Private Boundaries

### Reuse Upstream & Standard Library Over Bespoke Helpers
- **Upstream reuse**: Every public API symbol is a permanent maintenance liability under Hyrum's Law (`writings: stable-interface-paradox`, `tt-api-policy`). Prefer reusing standard library or upstream PyTorch (`torch.accelerator`) APIs over inventing bespoke framework APIs (`tt-api-design-guide`).
- **Stdlib constants & batch methods**:
  - Use `string.hexdigits` and `string.octdigits` (or `string.ascii_letters`, `string.digits`) instead of hand-rolling character strings (`"0123456789abcdefABCDEF"`, `"01234567"`).
  - Use `writer.writerows(data)` on `csv.writer` instead of looping `for row in data: writer.writerow(row)`.
  - Never call `re.compile(...)` inside a function if the compiled regex is only used once per call — either hoist the compiled regex to a module-level `Final` constant or call `re.match(pattern, s)` / `re.fullmatch(pattern, s)` directly, and check `is None` / `is not None`.
- **No fragile pre-validation regexes around CLI tools**: In shell scripts or wrappers around CLI tools (`uv`, `bazel`), do not write fragile pre-validation regexes (e.g., `^[0-9]+(\.[0-9]+)$` which breaks on free-threaded Python `3.13t`) when the underlying tool already validates its inputs (`gh-google-ml-infra-bap-50`).

### One Canonical Path, `__init__.py` Minimalism & No Redundant Module Symbol Aliases
- **Keep `__init__.py` minimal/empty**: Do not clutter package `__init__.py` with helper implementations, manual attribute re-exports from submodules, or inline imports requiring `# pylint: disable=g-import-not-at-top`. Move implementation helpers into a dedicated private submodule (`_internal`, `_loader`) and keep imports at the top of the file.
- **No redundant module-level symbol aliases (`Foo = imported_module.Foo`)**:
  - When a module imports another module (`from ... import metadata as custom_metadata`) and then defines a block of module-level aliases rebinding its symbols (`Rule = custom_metadata.Rule`, `RuleSet = custom_metadata.RuleSet`, `Vcs = custom_vcs.Vcs`), flag the alias block **right at its first line** (whether those aliases are used or unused in the file):
    > *"I don't think we need these aliases."*
- **Module hygiene**: Flag unprefixed module-level helpers, constants, or tables inside internal modules if they are not meant to be public, and remove unused module-level definitions, unused imports, or legacy shims .
- **Renaming unprefixed symbols in non-importable entrypoint modules (`__main__.py`)**: When an unprefixed function or symbol is renamed or removed inside a CLI entrypoint module like `__main__.py`, call attention to the fact that it is technically backwards-compatibility breaking under Hyrum's Law while noting that `__main__.py` is not intended to be importable. Recommend evaluating how widely used the package is and how many callers are likely to break: at a minimum, document the change, and if the package is widely used, consider keeping a deprecated alias/wrapper that emits a warning.
- **Private stdlib or external internal imports (`# pylint: disable=protected-access`)**:
  - Question reaching into another library's or CPython's private modules/attributes (such as `re._constants` / `re._parser`); ask if a public API exists.
  - When code imports private modules inside a `try: import ... except ImportError:` block with `# pylint: disable=protected-access,g-import-not-at-top`, anchor a comment right on the `import` line:
    > *"A comment to explain why exactly you need this access and why sometimes these things don't exist?"*
- **`@property` on public classes**: Prefix instance attributes with `_` and expose public state via `@property` (`tt-api-design-guide`).

### The "Attractive Nuisance" Doctrine
Reject features, configuration flags, or fallback mechanisms that look convenient but induce a high misuse-to-use ratio (`writings: attractive-nuisances`):
- **Never modify `LD_PRELOAD` or `os.execv` inside a library import**: Modifying `LD_PRELOAD` after the Python interpreter has already started is too late to change the C allocator and should never be done inside `__init__.py`.
- **No noisy import-time warnings for default user setups**: Do not emit runtime warnings on `import` when the user is running in the common/default configuration and cannot trivially change it.
- **Global mutation side effects in `__getattr__`**: Flag lazy module `__getattr__` implementations that mutate attributes globally upon first internal access in a way that silences `ExperimentalApiWarning` for subsequent user calls .

---

## 3. File I/O (`with open(path)`), String Construction, Polling Timeouts, Caching & Flags

### Prefer `with open(path)` & Explain Any Custom Binary/Chunked File Reader
- When a helper reads a UTF-8 text file using manual binary mode (`open(path, 'rb')`), chunked reads, `codecs.utf_8_decode`, or manual `\r\n`/`\r` newline normalization — and catches `(OSError, UnicodeDecodeError)` to return `None` (`def _read_*(path: pathlib.Path) -> str | None:`):
  - Anchor a comment right at the function definition asking **both** why `with open(path)` isn't used (or asking for an inline comment explaining why) and pushing to let errors propagate up instead of returning `None`:
    > *"Probably want to explain why we can't do this with just `with open(path)`?*
    > *And I usually prefer to let errors propagate up instead of returning `None`."*

### Multi-Line Strings (`textwrap.dedent`) & Section Joining (`"\n\n".join`)
- **Multi-line literals**: Flag multi-line strings built via backslash continuations (`"...\n" \`) or repeated `+` concatenation; recommend triple-quoted `"""..."""` strings with `textwrap.dedent`.
- **Joining document/prompt sections**: Avoid building strings in a loop via `+=` or slicing a joined multi-document string at a raw character index (`answer[:12000]`), which cuts off mid-word or mid-header. Instead, accumulate complete paragraphs into a `list` up to the character budget and call `"\n\n".join(sections)` at the end.

### Polling & Retry Loops Must Use `time.monotonic`
When reviewing retry or polling loops that take both `timeout_minutes` (or `timeout_seconds`) and `sleep_seconds`:
- **Bug pattern**: `for _ in range(timeout_minutes): ... time.sleep(sleep_seconds)` (or `range(sleep_seconds * timeout_minutes)`).
- **Fix**: Measure actual elapsed wall-clock time using `start_time = time.monotonic` and compare `time.monotonic - start_time < timeout_seconds`.

### `@functools.cache` Over Mutable Global Singletons
- Replace mutable global singletons (`_CLIENT = None` / `_POLICY = None` cached inside a caller function) with `@functools.cache` directly on the loader function (`get_client` / `load_policy`) (`gh-google-ml-infra-bap-29`).
- Warn if `@functools.cache` is applied to functions with unbounded high-cardinality arguments  or 0-arg functions that implicitly depend on `Path.cwd`.

### `absl.flags` Holders & Built-In Validators (internal_repo Python)
- Always assign `flags.DEFINE_*` calls to a module-level typed flag holder (`_OUTPUT_FILE = flags.DEFINE_string(...)`) so flag accesses (`_OUTPUT_FILE.value`) are statically type-checked.
- Use built-in `absl.flags` validators (`required=True` in `DEFINE_path`/`DEFINE_string`, `lower_bound=0` in `DEFINE_integer`) instead of writing manual validation boilerplate in `main`.

---

## 4. Exception Handling, Warnings & Defensive Invariants

### Propagate Exceptions — Never Return `None` or Swallow in Broad `except Exception:` / `except OSError:`
- **No error-sentinel `None`**: Do not return `None` or `False` on error; raise and propagate an exception (`gh-google-pytorch-torch_tpu-3894`).
- **No broad `try ... except Exception:`**: Flag functions that catch `Exception` just to log/print and continue or return a fallback. Let exceptions bubble up to the top-level entry point unless handling a specific, expected error type (`gh-google-ml-infra-bap-29`, `gh-google-ml-infra-bap-23`).
- **Validate-and-raise**: Prefer `_validate_sha256 -> None` (raising `ValueError` with expected and actual digests in scope) over `_verify_sha256 -> bool` .
- **`ValueError` vs `NotImplementedError`**: Raise `ValueError` (not `NotImplementedError`) for invalid argument values .

### Custom Warning Classes & Standard Warning Filters
- Define a project-specific warning hierarchy (`class TorchTPUWarning(UserWarning)` and specific subclasses) so users can control warnings via `PYTHONWARNINGS="ignore::..."` or `"error::..."` .
- Never track "has this warning been emitted?" with a manual global boolean (`_WARNED = False`). Python's `warnings` module handles "warn once" natively via warning filters (`"once"`).

---

## 5. CPython Set Intersection Performance & Pythonic Loop/Boolean Idioms

### Set Intersection (`bool(a & b)`) Over `any(x in b for x in a)`
- When checking whether any element of one collection is present in another (`return any(item in collection_a for item in collection_b)`):
  - Point out that if both are `Set`s (`set` or `frozenset`), you can write `bool(a & b)`!
  - Note the trade-off and empirical benchmark: while `any(x in b for x in a)` has the potential to bail early on the first match, `timeit` micro-benchmarking across random `frozenset`s shows `bool(a & b)` is ~6x faster (~121 ms vs ~735 ms) because set intersection runs entirely in C rather than stepping a Python generator loop.

### State Semantics, De Morgan's Law & Lazy Iteration
- **Observed state vs. assumed cause**: Name 404/absent states `GONE` or `NONEXISTENT`, not `ALREADY_DELETED` (`gh-google-pytorch-torch_tpu-3894`).
- **De Morgan's Law in `not in` checks**: Watch out for `if 'a' not in x or 'b' not in x:` (which is almost always `True`!) when `if 'a' not in x and 'b' not in x:` was intended.
- **Lazy iteration & early return**:
  - Use `zip(..., strict=True)` without redundant `list` materialization .
  - Prefer `for i, item in enumerate(seq):` over `range(len(seq))` indexing.
  - When finding the first matching index in a sequence, use early return (`for k, v in enumerate(cols): if v == name: return k`) or `next((k for k, v in enumerate(cols) if v == name), None)` instead of building an entire list comprehension `[k for k, v in enumerate(cols) if v == name]` first.

---

## 6. Voice & Framing Reference

Follow [references/voice-and-examples.md](references/voice-and-examples.md) when formatting review comments.
