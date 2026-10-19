# Runtime, Ownership & Tooling Semantics Fact Sheet (`pablogsal`) — Positive Facts the Reviewer Must Know (v5)

Negative anti-pattern lists did not stop recurring misconceptions; positive fact tables did (the era/API timeline eliminated every anachronism). Consult this sheet **before** drafting any comment that asserts or asks about a crash, leak, `AttributeError`/`NameError`, "cannot fail", "unused", missing check, ownership, fixture availability, or a convention. If a draft comment's premise contradicts a fact below, the comment is **not posted — not even as a question**. Asking the author to confirm a contract the reviewer is expected to know is noise.

---

## 1. Python data model & stdlib

| Fact | Consequence for review |
| :--- | :--- |
| Attribute lookup falls back from the instance `__dict__` to the class and its MRO. Deleting an instance attribute (`del self.x`, `__delattr__`) that shadows a **class-level default** makes reads return the class value; no `AttributeError` is raised. | Never claim `AttributeError` for a deleted/absent instance attribute when the class (or a base) defines it. A test that `del`s an instance attribute to exercise the class default is correct. |
| `ast` node **optional location attributes** (`end_lineno`, `end_col_offset`) have class-level `None` defaults (3.8+); mandatory ones (`lineno`, `col_offset`) are required for compilation. `ast.fix_missing_locations` fills missing mandatory ones. | Do not ask for `getattr(node, "end_lineno", None)` guards or claim a crash on nodes without end positions. Do not call optional attributes "mandatory" or vice versa. |
| `from mod import X as X` (and `__all__`) is the **explicit re-export idiom** required by PEP 484 / mypy `--strict` (`--no-implicit-reexport`) and pyright. | Never flag `import X as X` as redundant; a `[tool.mypy] strict = true` block in the same diff is the reason it exists. |
| Files holding binary formats (capture files, core dumps, pickles, wheels) are opened in binary mode (`"rb"`/`"wb"`); text-mode would corrupt them. A file opened **only to obtain its descriptor** (`.fileno()`) or to pass to a C function needs no particular text/binary mode. | Never suggest text mode or an `encoding=` argument for binary artefacts; never ask for binary mode where the diff already uses it or where only the descriptor is used. |
| A module imported under `try: … except ImportError:` that **existing tests already import the same way** is importable wherever those tests run. | Do not claim `NameError`/`ImportError` on another platform for such a module. |
| `sys.exit()` raises `SystemExit`; `raise sys.exit(...)` is wrong, but `sys.exit(...)` alone already propagates. `Py_Exit()`/`os._exit()` do not return. | Do not ask for `return` after them. |
| `contextlib.suppress`, `with` statements and `finally` run their exit code on exceptions; `try/finally` around a resource already owned by a context manager or a smart pointer is redundant. | Do not request `try/finally` for a resource that a `with` block, a destructor or a `shared_ptr` already releases. |
| Recursion over user data hits the recursion limit; a **per-path** cycle set bounds depth only, not total work. | Ask for a global visited set / total-visited bound (recall rule), but do not claim infinite recursion where a per-path set exists. |
| The REPL/doctest prefix is `>>> ` with `... ` continuations; documentation transcripts use them by design. | Do not flag the prefix itself; flag only prompts/continuations that are wrong or output that the code cannot produce. |

## 2. pytest, unittest & test harness facts

| Fact | Consequence for review |
| :--- | :--- |
| A test item's **fixture closure** includes every fixture requested transitively (fixtures requested by fixtures, `autouse` fixtures from reachable `conftest.py` files, `usefixtures` markers). | Do not claim a fixture is "not available" because the test function does not name it directly. |
| Legacy pytest wrappers are built on their modern counterparts (e.g. `testdir` over `pytester`, `tmpdir` over `tmp_path`); enabling the modern plugin enables the legacy fixture, and a test item's fixture-name list **is** the transitive closure, so checking for the modern name covers both. | Do not claim a gap between the two, do not claim `testdir` is unavailable when `pytester` is enabled, and do not ask the author to "switch" one for the other. |
| Test fixtures and sample data that mirror a sibling test's data are deliberate (same shapes make failures comparable). | Do not ask why fixture data duplicates a neighbouring test or suggest de-duplicating it. |
| `pytest.importorskip` imports the module at collection time; `importlib.util.find_spec` does not. | Prefer `find_spec` when importing has side effects (recall rule); do not claim `importorskip` fails to skip. |
| `@unittest.skipIf`/`skipUnless` decorators and `support.requires_*` helpers skip at collection; `self.skipTest` skips at run time. A skipped test is not a failure. | Do not call a skip "a test that cannot fail" — the counterfactual is about tests that **run** and still pass without the fix. |
| `test.support.script_helper.assert_python_ok` runs a fresh interpreter with isolated mode semantics: environment variables and `-X` flags must be passed explicitly. | Root-cause "fails on one platform" via isolation before proposing a skip. |
| `test_sys`-style `sizeof` tests encode struct layouts as **struct-format strings** by module convention (`check_sizeof(obj, size('…'))`). | Do not ask to replace the format string with `sys.getsizeof` math or a `ctypes` struct; it is the established format. |
| A subprocess test script communicates over the pipe/socket **defined in the same packet**; the matching read/write lives in the other script. | Before claiming an unbalanced handshake ("sends a message nobody reads"), locate the counterpart in the packet; if it is not in the packet, do not post. |
| Harness cleanup (`addCleanup`, fixtures' teardown, `subprocess` timeouts, `support.SuppressCrashReport`) already kills/cleans child processes and temp files. | Do not claim a hang or leaked process when the harness shown in the diff already handles it. |

## 3. CPython C-API & GC contracts

| Fact | Consequence for review |
| :--- | :--- |
| `PyType_GenericAlloc` (and `tp_alloc` for heap types) **tracks** instances of `Py_TPFLAGS_HAVE_GC` types; `PyObject_GC_New`/`PyObject_GC_NewVar` do **not** — the caller must `PyObject_GC_Track` after initialisation. | Do not ask "is this object tracked?" after `PyType_GenericAlloc`; do ask after `PyObject_GC_New` when fields are not yet valid for `tp_traverse`. |
| `tp_clear` and `tp_traverse` are **inherited** by subtypes (heap types included) and dispatched through the slot by the collector; `tp_clear` may run more than once and is not a destructor. | Do not ask whether a subclass "has" `tp_clear`; do ask when a `tp_clear` frees raw memory (move it to `tp_dealloc`). |
| Heap-type `tp_dealloc` ends with `tp->tp_free(self)` followed by `Py_DECREF(tp)`; `PyObject_GC_UnTrack` comes first. | Flag a direct `PyObject_GC_Del` or a missing type decref; do not ask for both `tp_free` and `GC_Del`. |
| Borrowed-reference accessors (`PyTuple_GET_ITEM`, `PyList_GET_ITEM`, `PyDict_GetItem`, `PyStructSequence_GET_ITEM`) cannot fail but the reference is only valid while the container is unchanged; fallible accessors (`PyTuple_GetItem`, `PyList_GetItem`, `PyObject_GetItem`, `PyDict_GetItemWithError`) return `NULL` on error. | The convention is **uniform checking** of fallible accessors in new code; request the `NULL`/error check directly even when the index is provably in range — never offer the unchecked `*_GET_ITEM` macro as an alternative. For borrowed references ask whether arbitrary code can run between fetch and use. |
| `PyLong_AsLong`/`AsSsize_t` return `-1` on error **and** on the legitimate value `-1`; `PyErr_Occurred()` disambiguates. | Do not claim a missing check when `PyErr_Occurred()` follows; do flag `-1` returns used without it. |
| `Py_UNREACHABLE()` marks a path the compiler may assume never executes (fatal error in debug builds). | Do not ask for a `return` after it or a "default" fallback. |
| Internal C APIs take **non-NULL arguments by contract** (filename, module name, buffer pointers); a silent default string or early return for a `NULL` argument hides caller bugs. | Never request a `NULL`-filename/`NULL`-argument fallback on an internal API; an `assert(arg != NULL)` is the most that is appropriate. |
| A conditional is **redundant** only when the exact same check dominates every path to it in the same function with no intervening call that could change the state; a check whose surrounding comments explain a partial-update or re-entrancy design is not redundant. | Do not call a check "redundant" without quoting the dominating check and the absence of intervening calls. |
| Specifier order in C/C++ declarations (`static inline` vs `inline static`, `const` placement) is formatter/style territory. | Never comment on it. |
| `PyErr_Clear()` after a failed optional lookup, and `PyErr_WriteUnraisable()` in `tp_dealloc`/callbacks, are the sanctioned ways to swallow errors in those contexts. | Do not call them "silent failure"; do flag a cleared error that should propagate. |
| The GIL (or a per-object critical section under `Py_GIL_DISABLED`) protects interpreter data structures, not application invariants. | Reason about free-threading races only with a quoted interleaving; do not assert "not thread-safe" without one. |

## 4. C++ ownership & RAII

| Fact | Consequence for review |
| :--- | :--- |
| A `std::shared_ptr` held by every object that yields access to a resource keeps the resource alive until the **last** owner is released, at which point the deleter (close/munmap/free) runs exactly once. | Do not claim a leak, double close, or dangling handle where the diff shows `shared_ptr` ownership; do not request `try/finally`/manual close around it. |
| `std::unique_ptr` has a single owner; `std::move` transfers it; the moved-from pointer is empty. | A moved-from `unique_ptr` dereferenced later is a bug; a destructor on a moved-from one is not. |
| `memcpy` of an object followed by flipping an `owns`/`valid`/`moved` flag on the source is the **ownership-transfer idiom**; the destination now owns the references/handles. | Do not claim a refcount leak or double free after such a transfer; quote the flag flip. |
| Destructors run at scope exit even when an exception propagates; `std::lock_guard`/`scoped_lock` release on every path. | Do not ask for manual unlock/release on error paths guarded by RAII. |
| A variable that is reassigned, incremented or decremented later in the same scope cannot be `const`. | Compile every `const` fence mentally against the whole scope before posting. |

## 5. Build, CI, packaging & docs conventions

| Fact | Consequence for review |
| :--- | :--- |
| CPython NEWS/What's New entries accept both imperative and past moods ("Fix …", "Fixed …"); `Patch by <Name>.` is the standard credit. A NEWS sentence that names the **user-facing feature or module** (e.g. the sampling profiler, `profiling.sampling`) is correct even when the changed file lives under a private `Modules/_…` or `Python/` path — the section follows the changed file, the sentence follows the user. | Never comment on NEWS mood or credit format; never "correct" a user-facing feature name to a private module or file name. |
| A user-facing limitation (platform support, unsupported modes) belongs in user-facing documentation (README, docs), not only in code comments or a maintainer file. | Never tell an author to move a limitation note out of the README; ask for it to be added there if missing. |
| The coverage-upload action used in these repositories runs the coverage tool itself when its gcov/include option is configured; a configured token is deliberate. | Do not ask whether coverage is collected or whether the token is needed when the diff configures them. |
| Compiler flag lines (`CXXFLAGS`, `CFLAGS`) that are **not in the diff** are out of scope. | Do not comment on them. |
| `setuptools`, `hatchling` and `flit` differ in how they source `version`, which files land in the sdist and how `license`/`license-files` are handled. | Quote the backend's documented default or ask; never assert a packaging consequence as a blocker. |
| A workflow trigger block copied from the repository's existing workflows is house style; community CI images are not personal images. | Do not flag them. |
| A rewrite of user-facing text is only an improvement if it is **strictly more specific** about what the user observes and introduces no private names. | Equal or vaguer rewrites are dropped. |

## 6. How to apply this sheet (the three-way gate)

For every draft comment that asserts or asks about a bug/leak/crash/"cannot fail"/"unused"/"missing":
1. **Proof quoted from the packet** (the diff line that establishes each premise, and no line that already handles it) → emit as a declarative at full severity, with a ```` ```suggestion ```` fence when the fix is one line.
2. **Premise is PR-specific and genuinely unknowable from the packet** (which of two defaults is intended, whether a deliberate removal had a reason, whether a follow-up is planned, whether a benchmark exists) → emit as a `question` that states the assumption.
3. **Premise is a general runtime, language, library, tooling or project contract** (anything in §1–§5, or a convention the reviewer could check) **or is contradicted by counter-evidence in the diff** → **do not post**. Not as a `minor`, not as a question, not as a "just to confirm".
