# Era, API Availability & Project-Process Fact Table (`pablogsal`) — Verification Reference (v5)

Every review comment that recommends an API, invokes a platform, or asserts a project convention must be checked against this table **before** it is written. If the fact is not here and not in the packet (`review_date`, `era_context`, diff), downgrade the comment to a tag question (*"…, no? (I may be missing something)"*) or delete it. Temporal/ecosystem miscalibration was the single largest source of false, high-severity assertions in `v1`.

---

## 1. CPython C-API & runtime availability (first release that has it)

| Symbol / feature | First version | Notes |
| :--- | :---: | :--- |
| `PyObject_CallNoArgs`, `PyObject_CallOneArg`, `PyObject_Vectorcall` (public) | 3.9 | before 3.9 use `PyObject_CallFunctionObjArgs` / `_PyObject_CallNoArg` (private) |
| `PyType_FromModuleAndSpec`, `PyType_GetModule`, `PyType_GetModuleState` | 3.9 | module-state heap types |
| `Py_NewRef`, `Py_XNewRef`, `Py_Is`, `Py_IsNone`, `PyModule_AddObjectRef` | **3.10** | in 2018–2021 code write `Py_INCREF(x); return x;` — never recommend `Py_NewRef` before 3.10 |
| `Py_TPFLAGS_IMMUTABLETYPE`, `Py_TPFLAGS_DISALLOW_INSTANTIATION` | 3.10 | |
| PEP 657 column tables, `co_positions()`, `PYTHONNODEBUGRANGES` / `-X no_debug_ranges` | 3.11 | |
| PEP 659 specializing interpreter, `Py_SETREF`/`Py_XSETREF` public | 3.11 / 3.12 | `Py_SETREF` was private (`pycore`) before 3.12 |
| C11 permitted by PEP 7 | 3.11 | C99 required from 3.6 (*"we use C99 now"* in 2019) |
| `PyUnstable_*` naming tier, `PyCode_AddWatcher`, `PyDict_AddWatcher`, `PyType_AddWatcher`, `sys.monitoring` (PEP 669), `-X perf`, `PyUnstable_WritePerfMapEntry`, PEP 701 f-strings, PEP 695 `type X = …`, `PyType_FromMetaclass` | 3.12 | |
| `PyMutex`, `Py_GIL_DISABLED` free-threaded build (PEP 703, experimental), `Py_mod_gil`, `sys._is_gil_enabled()`, `-X gil=0/1`, `_Py_DebugOffsets`, experimental JIT (PEP 744), PyREPL (PEP 762), `-X perf_jit` | 3.13 | free-threading becomes *supported* in 3.14 |
| PEP 768 remote debugging (`sys.remote_exec`, `pdb -p`, `_remote_debugging`), PEP 750 t-strings, PEP 758 bracketless `except`, PEP 765 `return` in `finally` warning, `support.subTests` | 3.14 | |
| PEP 799 `profiling.sampling` (Tachyon) / `profiling.tracing`, PEP 810 explicit `lazy import`, PEP 831 frame pointers by default | **3.15** | `profiling.sampling` is **not** in 3.14 even though PEP 768 is |

## 2. Python-level syntax & stdlib availability

| Feature | First version |
| :--- | :---: |
| walrus `:=`, positional-only `/` (PEP 570), `f"{x=}"` | 3.8 |
| `list[int]` builtin generics, `dict \| dict`, `str.removeprefix` | 3.9 |
| `match`, `X \| Y` unions at runtime, `zip(strict=True)`, parenthesised context managers (PEG), `dataclass(slots=True)` | 3.10 |
| `ExceptionGroup` / `except*`, `tomllib`, `typing.Self`, fine-grained tracebacks | 3.11 |
| PEP 701 nested f-strings, `itertools.batched`, `type X = …` | 3.12 |
| PyREPL default shell, `copy.replace`, free-threaded build | 3.13 |
| t-strings, bracketless `except`, `sys.remote_exec`, `support.subTests` | 3.14 |
| `lazy import`, `profiling.sampling` | 3.15 |

Projects with a Python floor below these versions (Memray 3.7+ in 2022, 3.8+ in 2023, 3.9+ in 2026; PyStack 3.7+/3.8+; pycrdt 3.8+) must gate the feature behind `sys.version_info` or not use it.

## 3. Tracker, process & convention facts (CPython)

- **Issue tracker**: `bpo-NNNNN` (bugs.python.org) until April 2022; `gh-NNNNNN` / `gh-issue-NNNNNN` afterwards. Never ask a 2020 PR for a `gh-issue` NEWS filename, never ask a 2024 PR for a `bpo-` title.
- **NEWS credit**: the standard trailer is `Patch by <Name>.` (or `Contributed by …` in What's New). Do not call it non-standard.
- **`Misc/ACKS`**: contributors add themselves in their own PR; maintainers do not police it in review unless the PR already touches it.
- **NEWS sections**: `Core and Builtins` for `Python/`, `Objects/`, `Parser/`, `Include/`; `Library` for `Lib/` and the `Modules/` C accelerators behind a stdlib module; others: `Documentation`, `Tests`, `Build`, `Windows`, `macOS`, `IDLE`, `Tools/Demos`, `C API`, `Security`. Do not prescribe a section from memory for an unfamiliar path — check where the user-visible behaviour lives.
- **PEP 7 braces**: braces are requested on every `if`/`for`/`while` body; the opening brace goes on the **same line** as a single-line condition, and PEP 7 explicitly allows it on **its own line** after a condition that spans multiple lines. PEP 7 does **not** mandate spaces around arithmetic operators, declaration-specifier order, or cleanup ordering. Never cite PEP 7 for anything outside braces, indentation, `if (` spacing, line length and comment style.
- **Backports**: `[3.x]` title prefix, `(cherry picked from commit …)` trailer, minimal diffs; never request signature cleanups or refactors in a backport.
- **Generated artefacts**: `Parser/parser.c` (from `Grammar/python.gram`, `make regen-pegen`), Clinic `*.c.h` (`make clinic`), `Python/generated_cases.c.h` (3.12+, `make regen-cases`). Review the source, verify the artefact is present.

## 4. Platform & tooling facts (Bloomberg repos and friends)

- **Memray**: launched April 2022 as **Linux-only** (`LD_PRELOAD`/`dlsym` allocator hooks, `/proc`, `ptrace`). macOS support arrived in early 2023; `attach` on macOS was being brought up in late 2022 with lldb-specific workarounds. Never assert macOS behaviour for a 2022 Memray PR unless the packet shows it; never claim Windows support.
- **PyStack**: Linux-only (ELF, `/proc/<pid>/mem`, `process_vm_readv`, ELF core files, libdw/elfutils). Supports glibc **and** musl (with dedicated wheel overrides). No macOS, no Windows.
- **pytest-memray / pytest-pystack**: pytest plugins; platform support follows the underlying tool. A Markdown/README limitation note about platform support is user-facing documentation — keep it there.
- **Bloomberg house style**: `d_` data members, `s_` statics, `LOG(DEBUG|INFO|ERROR)` macros, `GIVEN`/`WHEN`/`THEN` test sections, `tests/unit` vs `tests/integration`, `*_test_utils.pyx`, `*.test.js`. Not findings.
- **Build backends**: `setuptools`, `hatchling`, `flit` differ in sdist contents, license-file handling, dynamic version sources and `pyproject.toml` keys. Do **not** assert what a backend includes/excludes or how it reads `license`/`version` from memory; if the behaviour matters, quote the backend's documented default or ask.
- **CI services**: `codecov` tokens, `python-devs`/`quay.io` CI images, `cibuildwheel`, GitHub-hosted runners. An image or token the author configured deliberately is not a supply-chain finding; a trigger block copied from the repository's existing workflows is house style.
- **Debuggers**: `lldb` on macOS needs exact function-type casts for `expr`, DWARF (`dsymutil` while `.o` files exist, `-Og -g3`, no LTO) and `extern "C"` symbols outside namespaces; `gdb` on Linux uses `/proc` and `ptrace`; `process_vm_readv` requires `CAP_SYS_PTRACE` or same-uid + `ptrace_scope`.

## 5. How to use this table in a review

1. Read `review_date` and `era_context` first; write down the CPython branch (e.g. *3.9 main, 2020*), the C standard, the tracker era, and the project's Python floor.
2. Before recommending any symbol in §1–§2, confirm its first version ≤ the branch under review.
3. Before invoking a platform (macOS, Windows, musl), confirm §4 or the packet says the project supports it at that date.
4. Before asserting a convention (NEWS section, credit line, brace placement, ACKS, backend behaviour), find it in §3–§4; otherwise ask instead of asserting.
5. When the packet is ambiguous about whether an API has shipped in a released version, state the assumption in the comment (*"if this shipped in 3.14, we need …; if it is still only in main, ignore this"*).
