# CPython C API, PEG/Compiler, C++ Systems, Free-Threading, Unwinders & Build/CI Hygiene (`pablogsal`) — Pass 4 & 5 Reference (v5)

> **v5**: the clarity & micro-contract checklist runs on **every** modified hunk (not only silent ones; Python/Cython with the same weight as C/C++); layout/size hunks, the armed-feature counterfactual and `exec`-plus-value on compile-only tests are Tier 1 ledger items; fallible accessors get a direct `NULL`-check request (no macro alternative); eight more positive facts in [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md).

> **v4 rules**: three-way gate — proven in the diff → emit (fence for one-liners); author intent genuinely open → ask with the assumption stated; a general runtime/language/library/tooling contract or anything the diff contradicts → **do not post, not even as a question** (consult [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md)); mandatory second-look pass over every hunk that produced no comment (name-vs-body, declaration locality, regex readability, point-of-reliance comments, unchecked fallible accessors get a direct `NULL`/error-check request without reachability reasoning (never the unchecked-macro alternative), consumer-side accumulator overflow, tooling rationale); fences compiled against the whole scope; comments on unchanged or verbatim-moved lines dropped.

> **v3 rules**: no comment budget (every proven finding, every repeated-pattern anchor as its own one-line comment, and the central design objection are always emitted); proof by quotation before any bug/leak/crash/"cannot fail" claim, with `major`/`blocker` requiring a quoted diff line and assumption-dependent claims downgraded to `question`/`minor`; a stale-reference search after every deletion; every one-line change ships a ```` ```suggestion ```` fence; content nits (typos, stray `>>>` prompts, wrong example output) are posted, not deleted as formatting.

Condensed single-skill fallback for [`pablogsal-cpp-and-ml`](../pablogsal-cpp-and-ml/SKILL.md) (§0–5) and [`pablogsal-build-and-ci`](../pablogsal-build-and-ci/SKILL.md) (§6). All rules are grounded in `train_reference_public.jsonl` and `writings_and_talks_public.jsonl` (ids in parentheses). Check every API/platform/process fact against [era-api-timeline.md](era-api-timeline.md) before asserting it.

---

## 0. v2 additions: Pass 0, fallible-call table, lifecycle slots, layout, untrusted input
- **Pass 0 first**: deletions (`^-#define`, removed freelists/caches/pools/fast paths, `#if` blocks, asserts, log calls) → *"Why do we need to drop this? … no?"* + cost model + data ask on perf paths (*"not a blocker, but let's measure before landing so we know what we are trading"*); dead code (added fields/params/helpers with no second use); clarity layer (one-line comments on new `MAX_*`/limits like their neighbours, a comment at the point where code relies on a non-local invariant such as a buffer that must not be reallocated while a mode is active).
- **Fallible-call table** (ticked without reachability reasoning; request the `NULL`/error check directly — never *"or use the macro"*): list every `PyTuple_GetItem`/`PyList_GetItem`/`PyDict_GetItem*`/`PyUnicode_*`/`PyObject_*`/`PyLong_As*`/`PyMem_*`/`PyBytes_AsString`/`_PyCode_SetExtra`/unmarshal-compile helper/`fflush`/`close`/`mmap` call, tick checked/unchecked, **one comment per unchecked site** — *"`X` can fail here as well, no? We need to handle the error."* Finding one NULL dereference never ends the pass (`gh-python-cpython-109666`, `gh-bloomberg-pystack-126`, `gh-bloomberg-memray-257`, `gh-python-cpython-152331`).
- **Lifecycle slots**: `tp_clear` only breaks references (`Py_CLEAR`), may run more than once, is not a destructor — raw memory is freed in `tp_dealloc`; if `tp_clear` frees memory, **move** the free, do not `NULL` the pointer. Heap-type deallocs end with `tp->tp_free(self)` + `Py_DECREF(tp)`, never a direct `PyObject_GC_Del`.
- **Size & layout**: when `tp_basicsize`/`tp_itemsize`/`__sizeof__`/`sizeof`+`offsetof` arithmetic/`memcpy` lengths change, ask whether it stays in sync if either struct grows at the end and how it accounts for the variable-length tail; after a `memcpy` of an object, establish who owns the references before claiming a leak or double free.
- **Untrusted input**: every arithmetic op on a decoded value → overflow of the destination type? (wider integer, reject); every `i < n` → `i + 1 < n` loop-bound change → what happens to the leftover tail element? (prefer explicit rejection); bound-check every remote/mapped read.
- **Guardrails (v2)**: qualifier nits only on declarations the PR introduced or whose initialiser changed (moved-line discount); no speculative NULL/division/bounds guards without a named reachable path; no silent fallback values; no leak/double-free claims the diff already answers (ownership flag after `memcpy`, `shared_ptr`, harness kill); no anachronistic APIs (`Py_NewRef` 3.10+, `PyUnstable_*` 3.12+, `PyMutex` 3.13+); PEP 7 cited only for braces/indentation/`if (` spacing (own-line brace after a multi-line condition is allowed; no operator-spacing or specifier-order rule); Memray Linux-only at its 2022 launch, PyStack Linux-only.

## 1. CPython C API: Refcounts, GC Tracking, Allocation
- **Error paths**: an untracked `PyObject_GC_New` object cannot be `Py_DECREF`'d (*"This is going to fail because the object is not tracked."*); a tracked object must never be freed with `PyObject_GC_Del` (*"it overrides a bunch of cleanups like the call to `_Py_ForgetReference`"*). Allocate with `PyType_GenericAlloc`, `_PyObject_GC_TRACK` immediately, then `Py_DECREF` on every error path (`gh-python-cpython-27016`, `-26993`, `-27028`).
- **GC protocol**: `tp_traverse` **and** `tp_clear` on every `Py_TPFLAGS_HAVE_GC` type, even if cycles look impossible (`gh-python-cpython-17729`).
- **List contract**: never write borrowed refs or `NULL` holes into `ob_item`; `PyList_SET_ITEM`/`GET_ITEM` + `Py_INCREF`/`Py_DECREF`; `gc.get_objects()` exposes internal lists and a `<NULL>` slot segfaults (`gh-python-cpython-17729`). `__sizeof__` must not double count.
- **Arbitrary Python code**: `PyLong_AsLong`, `PyObject_Hash`, rich compare, `__del__` can mutate the container you iterate with a cached size → hold strong references or re-read sizes; validate everything before committing side effects; do not claim *"safe against arbitrary input"* otherwise (`gh-python-cpython-157228`).
- **Fallible calls**: check or assert `fflush`, `close`, `PyBytes_AsString` (`assert(PyBytes_CheckExact(...))`), `_PyCode_SetExtra` — publish state only on success (`gh-python-cpython-109666`, `gh-bloomberg-pystack-126`, `gh-bloomberg-memray-257`, `gh-python-cpython-152331`).
- **Visible cleanup**: `goto exit` + result variable so the lock release is obvious (`gh-python-cpython-109666`); no per-call heap allocation in hot helpers (`gh-python-cpython-99411`); `Py_Exit` does not return (`gh-python-cpython-125890`); `tp_del` → `tp_finalize` (`gh-python-cpython-27165`).
- **API shape**: symmetric `PyInterpreterState *interp` helpers (`gh-python-cpython-113584`); no `pegen` names in public headers (`gh-python-cpython-21016`).

## 2. PEP 7, Argument Clinic, C99
- Braces on every `if`/`for`/`while` body, brace on the `if` line, 4-space indentation, `if (` spacing — flagged on **every** hunk (*"Please, follow PEP 7 (add braces)."* ×9 on one PR; `gh-python-cpython-8726`, `-16788`, `-17729`, `-109666`, `-152331`).
- Argument Clinic for new C functions (link the HOWTO); Clinic cannot do `*args` (`gh-python-cpython-17729`).
- C99 designated initialisers for new `PyTypeObject`s (*"we use C99 now :)"*).
- Reject NUL bytes in the tokenizer, not the string parser (`gh-python-cpython-97577`).

## 3. PEG Parser, Grammar, AST, Locations
- Review `Grammar/python.gram`; `Parser/parser.c` is regenerated (`pep-0617`).
- Never change a working rule for an `invalid_*` rule; no enumerated token/operator lists; one rule → one error; specialised errors must be right for every valid program; justify `disjunction`/`expression_without_invalid` (`gh-python-cpython-123629`, `-157767`, `-133851`).
- Location spans: `(\n…\n)` wrapping shifts lines; `mode="eval"`; `end_lineno` swallowing comments is a compiler bug (`gh-python-cpython-112097`). PEP 657: `-1`/`None` public, `uint8_t` internal (`gh-python-peps-2022`).

## 4. Free-Threading, Locks, Fork, Re-entrancy
- **CPython**: re-read state loaded before `PyMutex_Lock` (*"`index` was loaded before taking the lock, so it can be stale"*); callbacks after unlock race with `Fini`; reuse `code_watcher_id >= 0` instead of registering again (8 slots, double decrement); remove `== 0` sentinel checks; ask whether `HEAD_LOCK` covers thread creation; refresh caches on `NULL` slots and growth; no `force_refresh` knobs (`gh-python-cpython-152331`, `-113584`, `-157732`).
- **Native trackers**: no Python code under the tracker mutex; no `Py_DECREF` of arbitrary objects under a Python-level lock; gate callbacks between `fork` and child reset; `finally` rollback for monkey-patches; do not retain frames past return (false leaks); same frame filtering on rebuild; `free_tool_id()` does not clear callbacks on 3.12/3.13 (`gh-bloomberg-memray-1031`, `-1033`).
- With the GIL held you *can* raise; decide whether it will be seen (`gh-bloomberg-memray-185`).

## 5. C++17/20 Systems Code (Memray, PyStack)
- `const` locals and methods (*"`const` fairy attacks again!"*), `explicit`, `override` without `virtual`, `~T() override = default`, brace-init/`emplace_back`, implementation-defined narrowing `size_t`→`int64_t`, `size_t` index types, shadowing, unused locals, `[this, &x]` captures, `std::array`, `.data()`, split assignment-in-condition, `if/else` over ternary chains, `<algorithm>` nits, `const&` callbacks, `reserve` (`gh-bloomberg-memray-257`, `-277`, `-317`, `-326`, `gh-bloomberg-pystack-31`, `-206`, `-185`).
- RAII & resources: `MAP_FAILED` guard before `munmap`, `noexcept` so `close()` is guaranteed, `unique_ptr`-owned mapping layer, assert reads stay inside the buffer, print before `abort()`, log failed `close()` (`gh-bloomberg-pystack-126`, `-206`, `gh-bloomberg-memray-277`).
- Cython: beware Python↔C bounce in one-liners; `except+` only where it can throw; templates vs virtual only if measured (`gh-bloomberg-memray-209`, `-277`).
- Binary reality: lldb needs exact function-type casts, DWARF (`dsymutil`, `-Og -g3`, no LTO) and `extern "C"` symbols; register numbers need provenance comments; musl overrides need comments; `_Py_DebugOffsets` over compiled-in offsets; frame pointers / JIT unwind info (`gh-bloomberg-memray-257`, `gh-bloomberg-pystack-32`, `-206`, `pep-0831`, `discourse-sc-jit-directive`).
- House style is not a finding: `d_`/`s_` prefixes, `LOG(DEBUG)`, `GIVEN/WHEN/THEN`.

### Annotated mini-examples (§1–5)
1. **`gh-python-cpython-26993`** — *"This is incorrect, this should still be `Py_DECREF`, `PyObject_GC_Del` cannot be called like that because it overrides a bunch of cleanups like the call to `_Py_ForgetReference`."*
2. **`gh-python-cpython-17729`** — *"Why are we setting this to `NULL`? If there is a `PyObject*` we would be leaking its reference, no? (I may be missing something)."* → REPL reproducer ending in `segmentation fault`.
3. **`gh-python-cpython-152331`** — *"`index` was loaded before taking the lock … Can we reload `extra_code_index` after acquiring the mutex? Same applies to `PyUnstable_PerfTrampoline_CompileCode`."*
4. **`gh-bloomberg-memray-1031`** — *"This runs the greenlet warning while holding `s_mutex`. A `sys.stderr.write` that starts and waits for another thread deadlocks … We cannot run this Python code under the lock."*
5. **`gh-bloomberg-memray-277`** — *"You can drop `virtual` here in all of these as you are already using `override`"*; *"Any reason why we are not just doing"* + brace-init fence.
6. **`gh-bloomberg-pystack-126`** — *"Let's mark this `noexcept` to make it clear that the `close` call before will always be called because this function does not raise"*; *"If `mmap` returned `MAP_FAILED` in the constructor we need to avoid this call"*.

## 6. Build Systems, CI, Packaging, NEWS, Docs & PEP Hygiene (v3)

Single-skill fallback for Pass 5 (see [`pablogsal-build-and-ci`](../pablogsal-build-and-ci/SKILL.md) for the full checklist). Audit every `Misc/NEWS.d/**`, `Doc/**/*.rst`, `pep-*.rst`, `Grammar/python.gram`, Clinic `*.c.h`, `Makefile.pre.in`/`configure.ac`, `setup.py`, `CMakeLists.txt`, `pyproject.toml`, `README*`, and `.github/workflows/*` file in the diff. Anchor on the NEWS filename, the sentence, the `Extension(...)` block, the deleted line, or the workflow condition; never bundle.

> **Verification gate (v2)**: before asserting anything about tooling, eras or project process, check the packet and [`era-api-timeline.md`](era-api-timeline.md) §3–§4. `Patch by <Name>.` is the standard NEWS credit; contributors add themselves to `Misc/ACKS` in their own PR; `Modules/*.c` accelerators behind a stdlib module go under `Library`; PEP 7's own example allows the opening brace on its own line after a multi-line condition and requires spaces only around assignment, Boolean and comparison operators; build-backend sdist/license/version behaviour is quoted from the backend's docs or asked. Unverifiable → tag question or delete. Severity follows verification.

### 6.1 `Misc/NEWS.d` blurb entries
- **Present** for every crash/race/leak/wrong-output fix (*"Please, add a NEWS entry for this crash fix."*, `gh-python-cpython-157228`). Not required for refactors, tests or typos.
- **Section** follows where the user-visible behaviour lives: `Python/`, `Objects/`, `Parser/`, `Include/` → `Core and Builtins`; `Lib/` and the `Modules/` accelerators behind a stdlib package → `Library` (*"this is a change in `Python/perf_trampoline.c`, so the NEWS entry should go in `Core and Builtins`, not `Library`."*, `gh-python-cpython-152331`). Map the changed file before prescribing a section; never prescribe one from memory.
- **Filename issue** is the issue the PR fixes, not a related blocker (`gh-issue-96670` vs `gh-97556`, `gh-python-cpython-97577`). `bpo-NNNN` before 2022, `gh-issue-NNNNN` after.
- **Wording** names the module users import with `:mod:`, lists every fixed symptom, and is updated when review adds a case (*"this should mention incorrect line numbers too, and better to name the user-facing module"*, `gh-python-cpython-157732`).
- **Prose that ships (v2)**: NEWS says what the user *observes*, not what the patch does; read it as a user and, if it took two reads, propose the sentence in a fence. `Patch by …` / ``(Contributed by … in :gh:`N`.)`` are the credit forms — never call them non-standard.
- **Doc/code mismatch is a question (v2)**: when docs/NEWS state one default and the code another, ask which is intended and offer the doc sentence as the default fix; never assert a regression or label it *blocker*.

### 6.2 `Doc/*.rst`, What's New and PEP text
- Supply the exact sentence in a `suggestion` fence: *"all leading whitespace characters will be omitted"* plus the matching `versionchanged` note (`gh-python-cpython-22469`).
- Fix PEP typos and missing commas the same way; say when a sentence was hard to read even if unsure of the rule (`gh-python-peps-1359`).
- Link the HOWTO from the reference entry (`Doc/howto/perf_profiling.rst`), turn prose enumerations into bullets, add design credit in What's New (`gh-python-cpython-96445`).
- **Discoverability (v2)**: when docs land in one place, ask where a user would look *first* (the function that accepts the flag, the module users import) and whether that place cross-references it; propose the one-line `:ref:`/`:func:` link.
- PEPs separate public contract from implementation detail (*"In the public API missing will return -1 in C and None in Python. The internal values are an implementation detail"*, `gh-python-peps-2022`).
- PEPs state what out-of-process consumers may rely on (*"they will remain self-contained"*, `gh-python-peps-1695`).
- Public headers and docs must not carry internal component names (`pegen`, `gh-python-cpython-21016`).

### 6.3 Every deletion is a question (v3)
- Grep the diff for `^-` lines that remove a mechanism: `Makefile`/`configure` lines and targets, compiler/linker flags, coverage or lint tool invocations, CI steps/jobs/matrix entries/triggers, test skips, `#define` limits or caches, doc sections.
- Unless the PR description justifies it, ask: `Why do we need to drop this? <what it still provides>, no?` — the train shapes are *"Why are we changing this rule?"* (`gh-python-cpython-123629`), *"Why was this just moved over here?"* (`gh-python-cpython-142655`), *"Is this needed for the fix?"* (`gh-python-cpython-122380`), *"We should fix those hangs or keep the free-threaded skip for now."* (`gh-bloomberg-memray-1033`).
- On allocation/call/tracing/import/build-time paths add the cost model and ask for data, open-handedly: *"I also would prefer not to have a heap allocation here for perf reasons but I am happy to discuss if we really need it."* (`gh-python-cpython-99411`), *"Maybe worth measuring the cost."* (`gh-python-cpython-122380`).
- Propose removals the PR has made obsolete (*"I think now you should be able to remove this supression …"*, `gh-python-cpython-19694`).

### 6.4 Regeneration, `configure`/`Makefile`, debug and observability flags
- `Grammar/python.gram` is the source; `Parser/parser.c` comes from `make regen-pegen`; Clinic `*.c.h` from `make clinic`; `make regen-all` must leave a clean tree (`gh-python-cpython-123629`, `gh-python-cpython-157767`).
- Review the source, verify the regenerated artefact is in the diff, never review generated C as authored.
- New C functions use Argument Clinic (except `*args`); new type objects use C99 designated initialisers (*"we use C99 now :)"*, `gh-python-cpython-17729`).
- `--with-pydebug` + `--huntrleaks` for refcount/GC work (`gh-python-cpython-16788`); detect build options via `sysconfig.get_config_var('PY_CORE_CFLAGS')`.
- Isolated-mode tests ignore env flags — root-cause a platform-only failure before skipping it (`gh-python-cpython-126166`); invalid `-X` options are silently accepted (`gh-bloomberg-pystack-206`).
- Observability is a build contract: `-X perf` perf-map files (`gh-python-cpython-109666`), `PYTHONNODEBUGRANGES` opt-out (`pep-0657`), frame pointers on by default in 3.15 (*"a single library without frame pointers breaks profiling, debugging, and tracing for the entire process"*, `pep-0831`), JIT builds must emit unwind info (`discourse-sc-jit-directive`).
- Question any flag change that trades debuggability for a sub-2% micro-gain.

### 6.5 Bloomberg native builds and packaging
- Every new `.cpp` goes in both `setup.py` `Extension(sources=…)` and `CMakeLists.txt` (*"Can you add this file to the `CmakeLists.txt`?"*, `gh-bloomberg-memray-257`).
- Injected/attach extensions must stay resolvable by `lldb`: no LTO + `-Og -g3`, run `dsymutil` while the `.o` files exist and ship the dSYM, `extern "C"` symbols outside the namespace, limited API (`Py_LIMITED_API 0x03070000`) kept clean (`gh-bloomberg-memray-257`). Only invoke a platform the project supported at the `review_date` (Memray was Linux-only at its 2022 launch; PyStack is Linux-only — [`era-api-timeline.md`](era-api-timeline.md) §4).
- `cibuildwheel` overrides (musllinux + custom elfutils) and architecture-specific unwinder constants carry explanatory comments (`gh-bloomberg-pystack-32`).
- `news/` fragments at the top level by preference (negotiable); question new towncrier templates; README stays user-facing and maintainer notes move to `MAINTENANCE.md` (`gh-bloomberg-pytest-memray-20`) — but a user-facing *limitation* (platform/version support) is user-visible information and stays in the README.
- A module-level backport import turns a test dependency into a runtime one (`gh-y-crdt-pycrdt-356`); prefer `find_spec` over collection-time imports (`gh-bloomberg-memray-1033`).
- Build-backend behaviour (`setuptools`/`hatchling`/`flit`: sdist contents, `license`, dynamic `version`) is quoted from the backend docs or asked — never asserted as a *blocker* from memory (v2).
- **Release-status check (v2)**: before asking for a deprecation alias or a NEWS entry for a renamed option/API, state the assumption that the old name shipped in a *released* version; an API that only lived in main needs neither.

### 6.6 CI workflows, buildbots and backports
- No hard-coded repository/branch values in workflows — forks *"can make a commit that customizes this file on their fork only"* (`gh-python-peps-1996`).
- **Conventions and explicit author setup win (v2)**: a trigger block that mirrors the repository's existing workflows is house style; a secret/coverage-upload token (e.g. `codecov`), container image or service the author configured deliberately is not a finding without a concrete failure; recognise well-known community CI images before calling them *personal* or a supply-chain risk.
- Buildbots across every tier platform stay green; a flaky test is a defect; release managers hold feature freezes (`pep-0619`, `pep-0664`).
- A matrix widened to 3.14t must have its hangs fixed or the skip kept (`gh-bloomberg-memray-1033`); pre-existing free-threaded failures a PR exposes still block it (`gh-bloomberg-memray-1031`).
- Backports: minimal diffs (*"so the diff stays minimal for the backport"*, `gh-python-cpython-157732`), never backport a test that fails on the target branch (`gh-python-cpython-16788`), `[3.x]` title prefix and cherry-pick trailer (`gh-python-cpython-27028`); never request signature cleanups or refactors inside a backport.
- PEP 7 in every C hunk: braces and 4-space indentation (`gh-python-cpython-152331`); brace on the same line as a single-line condition (`gh-python-cpython-8726`), own line allowed after a multi-line condition.

### 6.7 Only rewrite user-facing text if the result is better (v3)
A proposed NEWS/README/doc sentence must not introduce private module names, API field names or implementation detail; must use the correct section for the changed file; must keep user-facing limitations in user-facing docs; and must pass your own two-reads test. One sentence, one fence, anchored on the line it replaces (`gh-python-cpython-157732`, `gh-python-cpython-22469`).

### 6.8 Annotated examples
- **NEWS section + issue** (`gh-python-cpython-152331`, `gh-python-cpython-97577`):
  > *"Nit: this is a change in `Python/perf_trampoline.c`, so the NEWS entry should go in `Core and Builtins`, not `Library`."*
  > *"Nit: this NEWS entry is filed under `gh-issue-96670`, but this PR fixes `gh-97556`. Can we rename it so the changelog points to the right issue?"*
- **Doc precision** (`gh-python-cpython-22469`): the diff said *"the leading whitespace will be omitted"*; the fence replaces it with *"all leading whitespace characters will be omitted"*, and the `versionchanged` line with *"For string inputs, all leading whitespace characters are now omitted."*
- **Debuggable native build** (`gh-bloomberg-memray-257`): on the new `Extension` block —
  > *"lldb will fail to load the memray symbol if this is compiled with lto and with optimizations. To make it work I had to deactivate LTO and pass `-Og -g3` to it."*
  and on line 1 of the new source — *"Can you add this file to the `CmakeLists.txt`?"*
- **Deleted skip questioned (v2)** (`gh-bloomberg-memray-1033`): on the removed `pytestmark` —
  > *"This also enables the tests on 3.14t, where two of them time out locally and in CI. We should fix those hangs or keep the free-threaded skip for now."*
- **Fact checked, fact retracted (v2)** (`gh-python-cpython-17729`): after recommending Argument Clinic for a `*args` accelerator —
  > *"Oh, in that case, that won't be possible :( (I was under the assumption that https://bugs.python.org/issue20291 was resolved already). Apologies :)"*
  In `v2` that check happens before posting.

### 6.9 Noise to never emit (final pass with a delete action)
GitHub Actions SHA pinning or `permissions:` blocks; `CHANGELOG.md` where `Misc/NEWS.d`/`news/` fragments are the convention; *"use CMake/meson/hatch instead"* or Bazel/BUILD rules; ruff/black/isort/mypy config nits; Oxford-comma/double-space/EOF-newline/punctuation nits in prose; NEWS demands on refactors or tests; a NEWS section prescribed from memory; *"update the docs"* without the sentence; `Patch by`/`Misc/ACKS` claims; PEP 7 cited for arithmetic spacing or multi-line-condition braces; build-backend facts asserted without docs; *"personal image"*/supply-chain claims about community CI images; removal of a configured coverage token; restructuring a trigger block that mirrors existing workflows; moving a user-facing limitation out of the README; regression assertions on doc/code mismatches; comments on untouched lines without the `I know this pre-dates the PR, but …` framing; `gh-issue` filenames, `-X gil`, frame-pointer defaults or `profiling.sampling` before their era; dropping a proven finding, a repeated-pattern anchor or the central objection to keep the review short (there is no comment budget).

---

Voice: [voice-and-examples.md](voice-and-examples.md) · Era/API/process facts: [era-api-timeline.md](era-api-timeline.md). Standalone sub-skills: [`pablogsal-cpp-and-ml`](../pablogsal-cpp-and-ml/SKILL.md), [`pablogsal-build-and-ci`](../pablogsal-build-and-ci/SKILL.md).
