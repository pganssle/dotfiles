# Testing Rigor, GC/Refleak Hygiene & Test Validity (`pablogsal`) — Single-Skill Fallback Reference (v5)

> **v5**: the clarity & micro-contract checklist runs on **every** modified hunk (not only silent ones; Python/Cython with the same weight as C/C++); layout/size hunks, the armed-feature counterfactual and `exec`-plus-value on compile-only tests are Tier 1 ledger items; fallible accessors get a direct `NULL`-check request (no macro alternative); eight more positive facts in [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md).

> **v4 rules**: three-way gate — proven in the diff → emit (fence for one-liners); author intent genuinely open → ask with the assumption stated; a general runtime/language/library/tooling contract or anything the diff contradicts → **do not post, not even as a question** (consult [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md)); mandatory second-look pass over every hunk that produced no comment (name-vs-body, declaration locality, regex readability, point-of-reliance comments, unchecked accessors ticked without reachability reasoning, consumer-side accumulator overflow, tooling rationale); fences compiled against the whole scope; comments on unchanged or verbatim-moved lines dropped.

> **v3 rules**: no comment budget (every proven finding, every repeated-pattern anchor as its own one-line comment, and the central design objection are always emitted); proof by quotation before any bug/leak/crash/"cannot fail" claim, with `major`/`blocker` requiring a quoted diff line and assumption-dependent claims downgraded to `question`/`minor`; a stale-reference search after every deletion; every one-line change ships a ```` ```suggestion ```` fence; content nits (typos, stray `>>>` prompts, wrong example output) are posted, not deleted as formatting.

Condensed checklist for **Pass 3** of `pablogsal-code-review`. For the full standalone treatment load [`pablogsal-testing-and-mocks`](../pablogsal-testing-and-mocks/SKILL.md). All rules cite `train_reference_public.jsonl` record ids; era facts come from [era-api-timeline.md](era-api-timeline.md).

> **Completeness contract**: anchor one comment per uncovered `raise`, per fixture that cannot fail, per missing case from the issue, per skip that silently enables or hides a lane. *"I think we are missing a test that exercises this code path"* is posted once per anchor (`gh-bloomberg-memray-277` ×2), never once per PR.

> **Verification gate (v2)**: before asserting that a test is wrong, cannot fail, is missing, or leaks state, re-read the diff for counter-evidence (teardown, harness timeout/kill, sibling test file, class-level fixture, declared default). Traced mechanism → flat declarative; suspicion → *"…, no? (I may be missing something)"* / *"Please, double-check my logic :)"*; preference → `Nit:`. Never assert pytest/unittest internals from memory; never recommend `support.subTests` before 3.14, `sys.monitoring` before 3.12, or `-X gil` before 3.13.

---

## 1. Regression Tests Are Part of the Fix
- [ ] **Crash / race / leak fix ⇒ regression test**, with a concrete vehicle when the obvious one is blocked (*"compiling a `bytes` source with an embedded null"*) (`gh-python-cpython-97577`). Partial fixes name the remaining hole and still require the test: *"We need mutation-safe traversal and a regression test."* (`gh-python-cpython-157228`).
- [ ] **Every new `raise` / branch / fallback has a test** anchored separately (`gh-bloomberg-memray-277`); signature changes update every test call site (`gh-bloomberg-memray-439`); new JS helpers get `*.test.js` coverage; recursion over user data gets a deep-input test (`gh-bloomberg-memray-439`).
- [ ] **Every case named in the issue is covered** (*"This covers growth only. Can you add a test for the slot-fill case as well? Two workers is enough"*) (`gh-python-cpython-157732`); valid-input cases survive scope trims (*"Please keep these tests even if we trim the other cases."*) (`gh-python-cpython-157767`).
- [ ] **Dual code paths get an oracle test**: *"the **aggregated** data at the high watermark using both reporters is the same for some bunch of code examples"* (`gh-bloomberg-memray-277`); parser replacements prove AST equivalence over the stdlib (`pep-0617`).
- [ ] **(v2) A removed or simplified branch gets a test per affected surface**: construct one input where old and new differ, say which is right (credit the author if the new behaviour is better), then ask for a pin on *each* surface the branch served (both string kinds, both modes, both reporters) — one case per surface, each able to fail alone (`gh-bloomberg-memray-277`, `gh-python-cpython-157732`). A scenario named in the description but absent from the tests is a finding.

## 2. Tests Must Be Able to Fail
- [ ] **(v2) Counterfactual first — delete the fix mentally and run the test.** He states it as the acceptance criterion (*"it fails on this branch today"*, `gh-python-cpython-157732`; *"if I deactivate Neil's fix … should trigger the error (the callback is invoked), no?"*, `gh-python-cpython-16788`). Shapes that pass without the fix: the feature/plugin/flag under test is never armed in the inner run; only "no exception"/"returns" is asserted for a correctness or perf fix (ask to `exec` and check the value); a vacuously empty result loop (assert the length first); an input that never hit the bug; a fallback "forced" by reserving one slot when the code can pick another. Phrase: *"If we deactivate the fix, this test still passes, no?: \<reason\>"* + what would make it go red (template, not a quote) — only after the verification gate (does the harness already kill/clean up? does a sibling assertion cover it?).
- [ ] Fixtures/guards whose mechanism cannot fail: *"This will always succeed as an invalid `-X` option doesn't raise or warn. I am missing something here?"* (`gh-bloomberg-pystack-206`).
- [ ] Forced fallbacks really happen: reserve **all** candidate `sys.monitoring` tool ids (*"`2`, `3` and `4`"*) and *"assert we actually entered the profile fallback"* (`gh-bloomberg-memray-1031`).
- [ ] The test runs where the author thinks: isolated-mode embed tests ignore environment flags; fix the test rather than widen the skip (`gh-python-cpython-126166`).
- [ ] Post-error state is asserted when the design makes the object unusable: *"can we assert that finalize() raises ValueError after the TypeError?"* (`gh-python-cpython-157228`).
- [ ] Pre-existing failures exposed by a new helper (`@cython.profile(True)`) block landing: *"We still need to resolve them before landing."* (`gh-bloomberg-memray-1031`).
- [ ] Test lives in a sensible class (*"`TestFrameCaching` is a bit of an odd home for it"*) and obsolete workarounds (`suppress(PermissionError)` after moving to subprocesses) are removed (`gh-python-cpython-157732`, `gh-python-cpython-19694`).

## 3. Clarity Layer for Tests (v3)
- [ ] **Test names state the scenario**: `test_<func>_malformed_<node-kind>` / `test_<func>_<input>_<outcome>`, never `test_<func>_malformed` or `test_<func>_2` — the naming-precision rule (*"Sorry for the nit but i found the name a bit odd"*, `gh-bloomberg-memray-209`; *"so is clear what we are skipping"*, `gh-bloomberg-memray-326`) applied to tests. `Nit:` + proposed name.
- [ ] **Numbers copied from another language/module get a source-of-truth comment** (recursion depths, buffer sizes, table limits) or are imported, so they cannot drift — the provenance instinct of *"Let's add some comments here indicating where the register numbers come from"* (`gh-bloomberg-pystack-32`).
- [ ] **Non-obvious setup carries its why** (collector bracket, reserved ids, monkeypatched hooks, chosen timeouts) — ask for the comment in the code, do not narrate it in the review (`gh-python-cpython-16788`).

## 4. Dead Helpers & Leftover Global State (v3)
- [ ] Every helper, fixture, parametrisation value, constant or `conftest.py` hook **added** by the diff is used somewhere in the diff/context; otherwise *"Is this used anywhere? I cannot find another use in the diff"* / *"maybe we can drop it?"* (production precedent *"Non of these values are ever used, arent' they?"*, `gh-bloomberg-memray-277`; obsolete test workaround, `gh-python-cpython-19694`). Run this pass **before** bug hunting on large test rewrites.
- [ ] A new test that leaves `sys.modules`, codecs/hooks/profile functions, env vars, cwd, `atexit`/`register_at_fork` handlers or a claimed tool id behind gets `addCleanup`/`finally`/teardown or subprocess isolation (`gh-python-cpython-19694`); collection-time imports that flip global behaviour are probed with `find_spec` instead (`gh-bloomberg-memray-1033`).

## 5. GC, Refleak & Interpreter-State Hygiene (CPython)
- [ ] GC-timing tests start with `gc.disable()` and end with `gc.enable()` — hidden allocations under `--huntrleaks` otherwise trigger surprise collections (`gh-python-cpython-16788`).
- [ ] Make the scenario deterministic (e.g. an object in the same cycle that resurrects the weakref) and confirm it fails with the fix reverted — *"Please, double-check my logic :)"* (`gh-python-cpython-16788`).
- [ ] Extension-module tests build and import in a fresh interpreter via `assert_python_ok` so `sys.modules` stays intact (`gh-python-cpython-19694`); test-only C types in `_testcapimodule.c` follow PEP 7 braces (`gh-python-cpython-16788`).
- [ ] Tests travel with their fixes; never backport a test to a branch where it fails (`gh-python-cpython-16788`).

## 6. Test Doubles: Anti-Ceremony, Not Anti-Mock
- [ ] A `unittest.mock.Mock()` spy with `assert_not_called()` replaces a `nonlocal was_called` flag when it is the simpler falsification (`gh-python-cpython-16788`); never mock the collector, tracker, parser, writer, or debugger under test.
- [ ] CLI flags that are *"too cumbersome"* to test fully still get *"some smoke testing at least"* (`gh-bloomberg-memray-458`).
- [ ] Tests welded to internal object layout (ctypes corruption of `ob_item`) earn *"I am a bit hesitant because …"*, not a veto (`gh-bloomberg-pystack-194`).

## 7. Platform, Free-Threading & Collection Hygiene
- [ ] Replacing a version skip with `pytest.importorskip` can enable hanging `3.14t` lanes: *"We should fix those hangs or keep the free-threaded skip for now."* (`gh-bloomberg-memray-1033`).
- [ ] Probe optional modules with `importlib.util.find_spec(...)`; importing at collection time changes what unrelated tests exercise (`gh-bloomberg-memray-1033`).
- [ ] Free-threading-only tests carry `sys._is_gil_enabled()` / `PROCESS_VM_READV_SUPPORTED` / `skip_if_not_supported` guards (`gh-python-cpython-157732`).
- [ ] Frameworks by repo: `unittest` + `test.support` + `support.subTests` (3.14+) / `self.subTest` in CPython; `pytest` + `tmp_path`/`capsys`/`monkeypatch` + `GIVEN/WHEN/THEN` + unit-vs-integration split in Bloomberg repos; jest `*.test.js` for reporter assets. Memray was Linux-only until early 2023 — no macOS-lane assertions before the packet shows support.
- [ ] Flaky tests are defects; sanitizers and fuzzing are how re-entrant-finalizer bugs are found (`writings_summary_public.md` §1.7, `talk-europython-2024-obscure-bugs`).

---

## 8. Annotated Examples

### A. Crash fix without a test (`gh-python-cpython-97577`)
On `if (PyBytes_AsStringAndSize(t->bytes, &s, &len)) {` in `Parser/string_parser.c`:
> "This is a crash fix but it lands without a regression test. I know a `.py` file with a null byte is blocked by gh-96670, but can we still add a regression test somehow, e.g. compiling a `bytes` source with an embedded null? We really want to keep this from regressing."

### B. A fixture that always passes (`gh-bloomberg-pystack-206`)
```python
@pytest.fixture(autouse=True)
def enable_gil_if_free_threading(python, monkeypatch):
    _, python_executable = python
    proc = subprocess.run([python_executable, "-Xgil=1", "-cpass"], capture_output=True)
```
> "This will always succeed as an invalid `-X` option doesn't raise or warn. I am missing something here?"

### C. Spy instead of flag, collector bracket, counterfactual (`gh-python-cpython-16788`)
```python
        wr_callback_was_run = False
        def callback(wr):
            nonlocal wr_callback_was_run
            wr_callback_was_run = True
```
> "We can use a `unittest.mock` object here to simplify this logic:" *(diff → `callback = unittest.mock.Mock()` … `callback.assert_not_called()`)*

> "I will suggest starting the test disabling the collector, and end the test enabling it again so there are no surprising calls in the middle because hidden allocations when we don't expect (this tends to happen if the test runs with the `--huntrleaks`  in my experience)."

> "But if I deactivate Neil's fix for this problem, with the current state of the gc, the scenario that I described should trigger the error (the callback is invoked), no?"

### D. Skip replacement with side effects (`gh-bloomberg-memray-1033`)
```python
-pytestmark = pytest.mark.skipif(
-    sys.version_info >= (3, 14), reason="Greenlet does not yet support Python 3.14"
-)
+pytest.importorskip("greenlet")
```
> "This also enables the tests on 3.14t, where two of them time out locally and in CI. We should fix those hangs or keep the free-threaded skip for now."

> "Can we use `importlib.util.find_spec("greenlet")` here? Importing `greenlet` during collection makes subsequent trackers enable greenlet tracking, so this changes what unrelated tests exercise."

### E. Every case, red on the broken branch, and the test's home (`gh-python-cpython-157732`)
> "This covers growth only. Can you add a test for the slot-fill case as well? Two workers is enough, it is the second script in the issue and it fails on this branch today.
>
> Small nit: this runs both `cache_frames` modes, so `TestFrameCaching` is a bit of an odd home for it."

---

## 9. Never Emit (hard stops — delete before posting)
1. *"Add more tests"* / *"consider edge cases"* without naming the `raise`, input, case, or ids.
2. `pytest`/`hypothesis` in CPython, `unittest` in Bloomberg repos, adding or removing `GIVEN/WHEN/THEN`.
3. Mocks in place of `assert_python_ok`, real `gc.collect()`, real capture files, or real debugger attach; or a flag in place of a `Mock()` spy.
4. Type hints, docstrings or docstring wording, typing-syntax modernisation, import-order/placement, quote, EOF-newline or `encoding=` nits in test files.
5. A veto on a layout-sensitive memory-corruption test.
6. *"Missing test"* claims without checking `Lib/test/**` / `tests/**` in the same diff.
7. *"This test cannot fail"* without the mechanism (un-armed feature, vacuous assertion, wrong input) and without checking that the harness does not already kill/clean up what you think is unobserved.
8. pytest fixture-scoping/closure, plugin-arming or `unittest` loader facts asserted from memory.
9. Guards for states the test's own assertions, fixture types or parametrisation already exclude.
10. Comments on pre-existing test code without *"I know part of this pre-dates the PR, but …"* plus a correctness reason; cleanups in backport PRs; questions the description already answers.
11. Anachronisms (`support.subTests` < 3.14, `sys.monitoring` < 3.12, `-X gil`/`3.13t` < 2024, `gh-` < 2022, Memray macOS before the packet shows it).
12. Dropping a proven finding, a repeated-pattern anchor or a missing-case request to keep the review short — there is no comment budget; stand-alone praise comments.
