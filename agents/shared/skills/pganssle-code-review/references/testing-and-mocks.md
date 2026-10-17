# Pass 3: Testing Architecture, Test Doubles & Mutation Rigor

This reference details `pganssle`'s philosophy and review patterns for unit and integration tests, mocking discipline (`Real > Fake > Stub > Mock`), property-based testing (`hypothesis`), mutation testing mindset, fallback branch coverage, and pytest/unittest idioms. All cited examples come from `train_reference.jsonl` and `writings_and_talks.jsonl`.

---

## 1. The Test Double Hierarchy: `Real > Fake > Stub > Mock`

Based on `pganssle`'s talks and writings (*"Mocks and Stories: Test Doubles Practicing their Craft"* / the PRISMA testing model) and his code reviews (`gh-pypa-setuptools-2459`):

### Test Real Mechanisms First
- If real resources are cheap and checked in (such as golden files, `importlib.resources` lookups, `tmp_path` directories, or temporary local VCS repositories), test the real mechanism rather than mocking `importlib.resources`, filesystem calls, or `subprocess.run` (`tt-testing-skill`).
- **Do not mock `sys.platform` for unsupported platforms**: If a codebase exclusively runs on Linux, do not add mocks pretending `sys.platform == "darwin"` or `"win32"` just to test a platform guard.

### When Mocks Are Used: Mandatory Safeguards
1. **Always require `autospec=True`**: Whenever `mock.patch` or `MagicMock` is used, require `autospec=True` (or `create_autospec`) so signature mismatches fail immediately .
2. **Never mock logic under test or write no-op mock cleanup**:
   - Assert observable return values and state changes rather than internal `assert_called_with` expectations.
   - Flag no-op statements like `del mock_apply_gradients` — deleting the local variable reference in a test does *not* undo a `mock.patch`! .
3. **Encapsulate Lazy Global Cache Warmup in a Fixture**:
   - When mocking stdlib functions that interact with lazy process-global caches, do **not** scatter manual cache-warmup calls across individual test functions. Instead, create an `autouse` session/module fixture or a dedicated mocker fixture that warms the cache automatically before applying the patch (`gh-pypa-setuptools-2459`, `writings: mocks-and-stories-pytest`).
4. **Test-As-Installed**:
   - Prefer testing packages as installed wheels in isolated environments rather than relying on local working-directory imports or `sys.path` manipulation (`gh-pypa-setuptools-2315`, `gh-google-pytorch-torch_tpu-3894`, `writings: test-as-installed`).

---

## 2. Test Organization, `hypothesis` Property Tests, & `subTest` Parameterization

### Keep Tests in Cohesive Domain Test Files Mirroring Production Modules
- **Do not create fragmented single-feature test files**: If a PR adds serialization/copying support to an existing class, put those tests inside the class's existing test module (and property-test module) rather than creating a brand-new file just for that one operation.
- **Do not stuff multiple modules' tests into one giant test file**: Conversely, if a package has distinct submodules (e.g., an engine module and a metadata/parser module), split the unit tests into matching `*_test.py` files rather than putting 1,700+ lines of tests for multiple modules into a single test file; and do not add unrelated environment or allocator tests into a file dedicated to a specific loader (`op_testing.py` in ).

### Use `hypothesis` for Round-Trip & Copy Invariants
- Whenever a test suite verifies round-trip invariants (such as `pickle.loads(pickle.dumps(obj))`, `copy.deepcopy(obj)`, or reading/writing CSV/serialized formats where the test defines both a helper reader and writer), recommend property-based testing with `hypothesis`.
- **Clean stack traces in round-trip helpers**: Define a top-level round-trip helper function with `dumps` and `loads` on **separate lines** so stack traces immediately show whether serialization or deserialization failed.

### Refactor Repetitive Assertions & Loops into `subTest` or `parametrize`
- Flag repetitive blocks of assertions across directives/inputs or plain `for` loops inside tests :
  - Recommend defining a table `cases = [...]` and iterating with `with self.subTest(case):` (in `unittest`) or `@pytest.mark.parametrize` / `@parameterized.parameters` (in `pytest`/`absltest`).

---

## 3. Mutation Rigor, `except ImportError:` Fallback Coverage & Test Hygiene

### Mutation Check, Fallback Branches & Feature Strictness Coverage
- **Mutation check**: Flag any conditional branch (`if len(inputs.shape) == 1:`), counter increment (`self._step_count += 1`), or state flag (`self._episode_ended = False`) that can be negated or deleted without causing a test to fail .
- **Question `try: import ... except ImportError:` fallback coverage**:
  - Whenever production code includes a `try: import ... except ImportError:` block (especially one marked `# pragma: no cover` that sets a module variable to `None` to trigger a fallback path when the optional/private module is unavailable), emit a comment **right on the `except` fallback line** asking:
    > *"Do we have test coverage for both branches?"*
- **Test the strictness/distinguishing property of new features**: When a PR adds a stricter variant of an existing feature (e.g. a format directive with stricter delimiter rules, or a filter matching multiple token variations), verify there are negative tests proving that inputs violating the strict constraint raise `ValueError` and that all branches are exercised!

### Reject Opaque Binary Blobs & Giant Golden Files
- Reject checking in raw binary blobs (such as malformed binary data files) or huge static golden arrays when the test can construct the payload programmatically via a builder helper function or when the binary blob lacks comments explaining what exact corruption it tests .

### Unambiguous Timestamps in `freezegun` & Datetime Tests
- When a test freezes time with `freezegun.freeze_time(...)` using an ambiguous date-only string like `'2023-01-01'`, recommend spelling out the full unambiguous ISO-8601 timestamp with UTC offset: `'2023-01-01T00:00:00+00:00'`.

### `@pytest.mark.skipif`, `zip(strict=True)`, and Type Hints in Tests
- **Use `@pytest.mark.skipif` over conditional test bodies**: When a test only applies to Python 2 (e.g. testing `long`), decorate it with `@pytest.mark.skipif(six.PY3, reason="...")` instead of aliasing `long = int` or wrapping assertions in `if not PY3:` inside the test body (`gh-dateutil-dateutil-850`).
- **Use `zip(..., strict=True)` in tests**: In Python 3.10+ tests iterating over parallel expected/actual sequences, use `zip(a, b, strict=True)` and drop redundant `self.assertLen(a, len(b))` assertions.
- **Type hints & `Final` in test files**: Apply the same typing standards (function annotations on test helpers and `: Final[str]` on module constants) to new test files as to production code.
- **Defer device init**: Move runtime/device initialization (`_loader._init_device("tpu")`) into `setUp` rather than module top-level .
