# Reviewer Differences & Ecosystem Artifacts (`pganssle` vs. `wan` vs. `pablogsal`)

This document separates genuine preference differences among Paul Ganssle (`pganssle`), Zhanyong Wan (`wan`), and Pablo Galindo-Salgado (`pablogsal`) from apparent differences that come from the ecosystems they review in. By default, genuine differences resolve in favor of `pganssle`, and local project policy always takes precedence in existing repositories.

---

## Part 1: Genuine Style & Preference Differences

| # | Topic | `pganssle` (Default) | `wan` | `pablogsal` | Rule Applied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Import style (modules vs. symbols)** | Import modules (`from . import mod`, `import attrs`), except `collections.abc`, `typing`, `Path`. No `Foo = mod.Foo` aliases. | Allows `from ... import func as internal_func`. | Imports symbols directly (`from contextlib import suppress`, `from dataclasses import dataclass`). | Import modules, not symbols (except `collections.abc`, `typing`, `Path`). |
| **2** | **Mock spies vs. `autospec=True`** | `Real > Fake > Stub > Mock`; check state/returns; `autospec=True` required on every mock. | Directionally aligned (`Real > Fake > Stub > Mock`; bans `MagicMock` data objects and brittle call-count checks). | Sometimes uses bare `callback = Mock()` + `assert_not_called()` without `autospec=True`. | Follow `Real > Fake > Stub > Mock` and always pass `autospec=True` whenever any mock is used. |
| **3** | **Testing private helpers** | Test only the public contract; never test `_` helpers directly. | Sometimes asks for direct unit tests of non-trivial internal helpers and exposes `_DEFAULT_*` constants for tests. | Agrees with `pganssle`: tests public/CLI contracts and avoids testing internal layout details. | Test only the public contract; extract a dedicated submodule if an internal engine needs direct tests. |
| **4** | **Config files vs. module constants** | Pull repo paths, layout maps, exclusion regexes, and size limits into a root config file so tools stay generic. | Keeps tool defaults as module-level `Final[Sequence[str]]` tuples. | Avoids hardcoded repo/branch names in workflows; likes table-driven config dicts. | Put repo-specific paths, exclusions, and limits in a root config file; keep only true domain invariants as `_`-prefixed `Final` constants. |
| **5** | **`NotImplementedError` vs. `TypeError` / `ValueError`** | Follows the Python spec: `ValueError` for bad argument values; `NotImplementedError` only for abstract/unfinished methods. | Uses `NotImplementedError` for unimplemented hardware/backend capabilities; `ValueError` for bad args. | Used `NotImplementedError` on Memray reader accessors that are unsupported by design on aggregated captures (outside Python's documented spec). | Follow Python's `exceptions` spec: `ValueError` for bad values, `TypeError` (or a custom domain error) for operations unsupported by design, and `NotImplementedError` only for abstract methods or unfinished features. |
| **6** | **C++ `const` on value params & locals** | Rust-style `const`-by-default: everything `const` unless mutation or `std::move` is required. | Google/Abseil style: omits top-level `const` on value params in `.h` declarations (Abseil Tip #109); never marks movable locals `const`. | Agrees with `pganssle` in C++: marks every non-mutated local and read-only method `const` (never scalar locals in pure CPython C). | Mark every C++ local, parameter, and method `const` unless mutated or moved from; yield to local project style (such as Abseil Tip #109 in `.h` headers) in existing repos. |
| **7** | **`Optional[T]` vs. `T \| None` in existing files** | Writes `T \| None` and `A \| B` in new code/files; never mixes unrelated typing churn on untouched lines into a PR. | Keeps `Optional[T]` on new code in a file if that file already imports `Optional`. | Avoids typing-syntax churn on untouched lines. | Write `T \| None` and `A \| B` in new code and modified signatures; never touch unrelated lines in a functional PR (do whole-file upgrades in a separate PR). |

---

## Part 2: Context, Era & Ecosystem Artifacts (Not True Disagreements)

| Topic | Why the Review Corpora Looked Different | Consensus Rule |
| :--- | :--- | :--- |
| **Type hints in stdlib & tests** | `pablogsal` reviews CPython `Lib/` (which forbids type hints) and Bloomberg tools (which require them). All three reviewers follow local project policy. | Annotate every function, method, `@property`, script, `Final` constant, and test helper by default; yield to local project policy (such as CPython `Lib/`). |
| **Test framework (`pytest` vs. `unittest`)** | `wan` works in monorepo `absltest` / C++ `GoogleTest`; `pablogsal` works in CPython `unittest` and Bloomberg `pytest`. | Default to `pytest` + `hypothesis` + fixtures + `parametrize` + `tox` unless the repository mandates `unittest` / `absltest`. |
| **Python build backends** | `pganssle` defaults to `flit` because it is the simplest pure-Python backend and avoids `setup.py` whenever possible. Older C++ extension repos used `setup.py` + `CMakeLists.txt` only before modern PEP 517 native backends matured. | Default to `flit` for pure-Python packages and `# /// script` (`uv`) for standalone scripts. Avoid `setup.py`; for compiled C/C++ extensions, pick a modern backend (`meson-python`, `hatch`, `scikit-build-core`, or `bazel`) case by case. |
| **`attrs` vs. `dataclasses`** | `pganssle` uses `@dataclass(frozen=True)` or `@attrs.frozen` where `attrs` is already present; `pablogsal` avoids adding third-party model deps when stdlib suffices. | Default to `@dataclasses.dataclass(frozen=True)` in stdlib-only projects; use `@attrs.frozen` when `attrs` is already a dependency. Never use `NamedTuple` for domain records. |
| **`StrEnum` vs. `Enum`** | `StrEnum` appears frequently in `pganssle` reviews because enums often cross string communication layers (CLI flags, serialization). | Use `enum.Enum` by default; use `enum.StrEnum` (3.11+) when string representation is needed at a communication boundary. Never write `(str, Enum)` in 3.11+. |
| **GitHub Actions SHA pinning** | `zizmor` requires 40-char SHA pins; older workflows without pins simply predate that requirement. | Pin all third-party `uses:` actions to 40-char SHAs with `# vX.Y.Z` comments, and configure automatic updates (Dependabot / Renovate) or add a `TODO` explaining how to keep pins updated automatically. |
| **C / C++ style dialect** | Each runtime has its own house style (CPython PEP 7 vs. Google/Abseil C++ vs. standalone C++17/20). | Follow PEP 7 + C-API contracts in CPython C; Google C++ + Abseil in monorepo/PyTorch/TorchTPU C++; and repo naming + strict RAII/Rust-style `const`/`explicit`/`override` in standalone C++17/20. |

---

## Harmonized Patterns Across All Three Reviewers

- **Exception suppression**: Let exceptions propagate by default. When a narrow, specific exception is genuinely expected and intentionally ignored (such as `FileNotFoundError` during optional cleanup), write `with contextlib.suppress(FileNotFoundError):` instead of `try/except: pass`.
- **Error message checks in tests**: Escape regex metacharacters (`re.escape(...)`) or compare exact strings on short literal error messages; match essential keywords/field names and verify post-error state on multi-sentence diagnostics.
- **Docstrings and comments**: Use third-person declarative verbs (`Returns...`, `Sets...`), explain *why* and non-local invariants rather than narrating code, link issues on `# type: ignore[code]`, and use `re.VERBOSE` with sample inputs on complex regexes.
