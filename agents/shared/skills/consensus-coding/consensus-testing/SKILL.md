---
name: consensus-testing
description: >-
  Writes and refactors Python and C++ tests to satisfy pganssle, wan, and
  pablogsal, defaulting to pganssle on test-stack choices. Covers testing only
  the public contract, Real > Fake > Stub > Mock with mandatory autospec=True,
  pytest + hypothesis + fixtures, counterfactual mutation checks, global-state
  isolation, and GoogleTest/gMock/FuzzTest conventions. Use whenever writing or
  updating tests.
---

# Consensus Testing (`pganssle` + `wan` + `pablogsal`)

Write tests that prove behavior through the public contract and fail reliably whenever production logic breaks. Never write tests that merely mirror implementation steps or pass vacuously.

## 1. Public Contract & Coverage Target

- **Test only the public contract** (`pganssle` default): Call public functions, methods, CLI entrypoints, and classes. Never import `_`-prefixed helpers or strip leading underscores just to unit-test internals. If an internal engine is complex enough to need direct tests, extract it into a dedicated submodule with its own clean contract.
- **Aim for 100% branch and line coverage** through public APIs. Every new `if/else` branch, `raise` statement, and `except ImportError:` fallback must be exercised by a test.
- **Hunt for edge cases**: Empty containers, single-element inputs, boundary numbers (`0`, `-1`, `MAX`), duplicate elements, Unicode/non-ASCII text, timezone/DST boundaries, and malformed inputs.

## 2. Test Doubles Hierarchy (`Real > Fake > Stub > Mock`)

Always pick the highest level in this hierarchy that works:

1. **Real object**: Real dataclasses, `tmp_path` files, in-memory SQLite, or real pure-Python objects.
2. **Fake**: A lightweight in-memory implementation of the same `Protocol` or interface (`FakeClock`, `FakeStorage`).
3. **Stub**: A minimal object returning fixed canned values.
4. **Mock**: Last resort, used only at process, network, or hardware boundaries.

### Mandatory Mock Rules
- **Always pass `autospec=True`**: Every `mock.patch(..., autospec=True)` and `mock.create_autospec(Spec)` must enforce the real signature so typos or signature drift fail immediately.
- **Never mock the unit under test**: Only mock external collaborators.
- **Never use `MagicMock` as a data record**: Construct the real `@dataclass`, proto, or config object instead.
- **Verify state and return values, not call counts**: Assert on returned data or observable state changes. Use `assert_called_*` / `assert_not_called()` only when emitting (or suppressing) the external side effect *is* the contract.

## 3. Mandatory Counterfactual & Mutation Check

Before considering any test complete, perform this mental check:

- **Delete or invert the fix**: Mentally delete the guard clause, state reset, or calculation under test. If the test still passes, strengthen the assertion until it fails.
- **Verify the feature is armed**: In profiler, compiler, or plugin tests, assert that the profiler/plugin was active before asserting that zero errors occurred.
- **Execute generated code**: In AST, compiler, or codegen tests, do not stop at `compile()` succeeding — `exec()` or evaluate the result and assert the computed runtime value.
- **Guard loops against empty results**: Before asserting inside `for item in results:`, always assert `assert results` (or `assert len(results) == expected`) so an empty collection never passes silently.
- **Pre-populate output targets**: When testing `clear()`, `reset()`, or `ToProto(..., &out)`, pass a non-empty `out` object to prove stale fields are wiped.
- **Oracle / equivalence tests**: When maintaining a fast C/C++/lowered path alongside a reference Python/eager path, test that both produce identical outputs across shared inputs.

## 4. Python Test Stack & Idioms (`pytest` + `hypothesis`)

Default to `pytest`, `hypothesis`, fixtures, `@pytest.mark.parametrize`, and `tox` unless the target repository mandates `unittest` (such as CPython `Lib/test/`).

- **Fixtures over class inheritance**: Never share setup through `TestCase` base classes or mixins. Write composable `@pytest.fixture` functions.
- **Parametrize table-driven tests**: Use `@pytest.mark.parametrize("input_val,expected", [...])` (or `with self.subTest(...):` in `unittest`) instead of copy-pasted test functions.
- **Property-based testing (`hypothesis`)**: Use `@given(...)` for parsers, formatters, serializers, and mathematical invariants. In round-trip tests, put encode and decode on separate lines:
  ```python
  @given(st.text())
  def test_token_round_trip(raw: str) -> None:
      encoded = codec.dumps(raw)
      decoded = codec.loads(encoded)
      assert decoded == raw
  ```
- **Scenario-based test names**: Name tests `test_<unit>_<scenario>_<expected_outcome>()` (for example, `test_load_config_missing_file_raises_config_error`).
- **Error message assertions**:
  - For short literal error strings, escape metacharacters (`pytest.raises(ValueError, match=re.escape(expected))`) so `.` or `(` cannot match unintended text.
  - For multi-sentence diagnostics or deprecation warnings, match the essential field name or keyword and assert post-error object state.

## 5. Isolation, Global State & Determinism

- **Clean up global state**: Restore `monkeypatch` env vars, `sys.modules` entries, global registries, and `sys.monitoring` tool IDs in fixtures or `addCleanup`.
- **Subprocess isolation for process-global effects**: Test import-time side effects, signal handlers, `fork()`, and fatal C-API paths in a clean `subprocess.run([sys.executable, "-c", code], check=True)` (or `assert_python_ok` in CPython).
- **Resource exhaustion fallbacks**: When testing fallback paths for limited slots (such as `sys.monitoring` IDs), explicitly occupy all candidate slots in the test and assert the fallback ran.
- **GC & refcount determinism**: Wrap deterministic garbage-collection assertions in `gc.disable()` and `try: ... finally: gc.enable()`.
- **Unambiguous timestamps**: Pass explicit ISO-8601 UTC strings (`"2026-01-15T08:30:00Z"`) to `freezegun` or fake clocks — never `"01/02/03"`.
- **Programmatic inputs over binary blobs**: Build binary or protocol inputs via small helpers in the test rather than committing opaque `.bin` fixtures; assert targeted log records (`caplog`) instead of diffing full log files.

## 6. C++ GoogleTest, gMock & FuzzTest Rules

When writing C++ tests with GoogleTest and gMock:

- **Stub with `ON_CALL`, not `EXPECT_CALL`**: Use `ON_CALL` + `NiceMock<MockFoo>` to configure collaborator return values; reserve `EXPECT_CALL` for external side effects whose call count is the contract.
- **`EXPECT_*` over `ASSERT_*`**: Use `EXPECT_*` so a single test run reports every failure. Use `ASSERT_TRUE(status.ok())` or `ASSERT_NE(ptr, nullptr)` only immediately before calling `status.value()` or dereferencing `ptr`.
- **Argument order**: Write `EXPECT_EQ(actual, expected)` (actual first, expected second).
- **Floating-point checks**: Use `EXPECT_DOUBLE_EQ`, `EXPECT_FLOAT_EQ`, or `EXPECT_NEAR` — never `EXPECT_EQ` on floats.
- **Loop context**: Put `SCOPED_TRACE(test_case.name)` inside table-driven loops and assertion helpers.
- **Fuzzing**: Add `FUZZ_TEST` targets for C++ parsers, decoders, and shape-inference logic.

## Quick Checklist Before Finishing Tests
- [ ] Tests exercise only the public contract and cover every new branch, error raise, and `ImportError` fallback.
- [ ] Doubles follow `Real > Fake > Stub > Mock`; every mock uses `autospec=True`; no `MagicMock` data records exist.
- [ ] Deleting or inverting the production change causes at least one test to fail (counterfactual check).
- [ ] Loops assert non-empty results before iterating; compiler/codegen tests execute and verify output values.
- [ ] Global state (`sys.modules`, env vars, tool IDs, GC) is restored cleanly or isolated in a subprocess.
