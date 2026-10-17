# Pass 4 & Pass 5: C/C++, TorchTPU/ML Compiler Nuances, Build Hermeticity, CI/CD & VCS Hygiene

This reference details `pganssle`'s patterns for reviewing C/C++ extensions, Python C-API code, PyTorch/TorchTPU/XLA compiler integrations, Bazel/Python build systems, Copybara, CI/CD workflows, supply-chain security, and PR hygiene. All cited examples come from `train_reference.jsonl` and `writings_and_talks.jsonl`.

---

## 1. C / C++ & Python C-API Safety

### Signed Integer Bounds Checking (`< 0` AND `>= len`)
Whenever C, C++, or Python buffer-parsing code checks an index upper bound (`idx >= count`), verify whether the index is a signed integer type (`int`, `int64_t`, `ssize_t`, or Python `int`) and ask whether `idx < 0` also needs to be handled.

### Python C-API Reference Counting & Initialization
- In CPython C extensions (`PyLong_FromLong`, `PyObject_GetAttr`), audit every conditional branch and early error exit to ensure `Py_DECREF` is called before returning (`gh-pganssle-zoneinfo-97`).
- Check that C-API capsule imports (`PyDateTime_IMPORT`) verify `PyDateTimeAPI != NULL` and jump to error handling on failure.

### Eager Invariant Validation at Load Time
Validate binary/input invariants eagerly once at load/construction time (especially when the loaded object is cached) rather than deferring checks to point-of-use.

---

## 2. PyTorch / TorchTPU / ML Compiler Specifics

### Testing Python-to-C++ Runtime Integration & Sentinels
- When a C++ extension consumes runtime configuration or version info populated by Python (e.g. setting the `libtpu` version from `_loader.py`), prefer testing the integration from a Python test (`env_test.py`) rather than setting the value artificially from a C++ unit test.
- Use an explicit sentinel value to distinguish between "package is not installed" and "initialization function was never called" to aid debugging.

### C++ Value Categories, Threading, & Operator Lowering
- **Avoid unnecessary copies & dangling captures**: Pass non-trivial C++ types by `const &`, use `std::move` when transferring ownership, and check that C++ lambda captures (`[&]`, `[this]`) in deferred/async execution cannot outlive referenced objects (`reviewing_code/SKILL.md`).
- **`ThreadLocalDebugInfo` over bare C++ `thread_local`**: Never use bare C++ `thread_local` to store per-Python-thread state in PyTorch/TorchTPU; use `c10::ThreadLocalDebugInfo` (`tt-context-managers`).
- **Buffer donation (`DispatchOpOut`)**: Verify that all out-variant (`Aten*Out`) and in-place (`Aten*Inplace`) operators use `DispatchOpOut` (`reviewing_code/SKILL.md`).
- **Virtual capability parity (`#ifdef` / `#else`)**: When adding a capability override like `bool supportsWindow const override { return true; }` on one class or `#ifdef` branch, check that sibling classes or `#else` branches define the corresponding `return false;` override .
- **Error macro formatting (`TT_CHECK_THROW` vs `TT_CHECK`)**: User-facing precondition checks must use `TT_CHECK_THROW` (lowercase start, no trailing period, no op-name prefix, `"expected X, got Y"`), while internal compiler invariant checks must crash immediately via `TT_CHECK` / `ABSL_CHECK` (`tt-error-guide`).

---

## 3. Build Hermeticity, Bazel & Clean Tool Boundaries

### Bazel Hermeticity & User-Representative Test Environments
- **Fully hermetic builds**: Reject ad-hoc `pip install`, host `/usr/lib` library scraping, or post-build wheel splicing inside shell scripts when Bazel or `nox` should orchestrate the build hermetically (`gh-google-pytorch-torch_tpu-3552`, `gh-google-pytorch-torch_tpu-2353`).
- **Do not mutate library paths or defaults in `build_defs.bzl`**: Do not modify `LD_LIBRARY_PATH` or set non-standard allocator defaults in Bazel test macros in ways that diverge from how real users run the package — tests should run as if we were a user.
- **internal_repo `BUILD` hygiene (`exports_files` & `pytype_strict_library`)**:
  - Flag `exports_files([...])` blocks that export internal `.py` module or test files which no other package should consume directly as raw source files.
  - Prefer `pytype_strict_library` (from `//tools/build_defs/python:pytype.bzl`) over raw `py_library`.
- **Single responsibility for scripts & test files**: Do not bury unrelated environment setup inside a script dedicated to running `bazel-diff`, or put unrelated tests inside a narrow test module .
- **Explicit CLI flags & scheduler-friendly lifecycles**: Prefer explicit CLI flags over ambient env vars , file-path flags over raw JSON strings (`gh-google-ml-infra-bap-23`), and letting external cron schedulers manage intervals rather than `time.sleep(interval)` at the end of `main` .

---

## 4. CI/CD Workflows, Formatters, Copybara & Supply Chain Security

### Linter Workflows & Formatter / Copybara Interaction
- **Consolidate linter workflows**: Prefer adding a job or step to an existing `lint.yml` workflow (named accurately, e.g. `"Run code linters"` rather than `"formatting"`) over proliferating separate `.github/workflows/*.yml` files (`gh-google-pytorch-torch_tpu-3443`).
- **Copybara `pyformat` vs. external formatters (`ruff format`)**: In internal_repo repositories exported via Copybara (`torch_tpu`), remember that Copybara automatically formats code with `pyformat` on import and export. Question enabling `ruff format` in CI unless it is verified to produce identical output to `pyformat`, and note that running a file-level formatter on modified files in CI will reformat untouched lines in those files.
- **Clean `pyproject.toml` & `.bzl` formatting**: Flag commented-out config lines or unused tool sections (such as `[tool.ruff.lint.isort]` when import sorting isn't enabled) in `pyproject.toml`, and question generated `.bzl` files that are collapsed onto a single giant unformatted line.
- **Copybara configuration (`copy.bara.sky`)**:
  - Question removing `patching_enabled = False` (when the package carries no patches), removing test files (`conftest.py`) from `git_files`, or removing `version_selector` semver rules.
  - When `noop_behavior = "IGNORE_NOOP"` is used on a `core.transform` block to stage a migration, ask to add a `TODO` to remove the `IGNORE_NOOP` (*"We should add a TODO to remove the IGNORE_NOOP."*).

### Supply Chain Security, Artifact Globs & CI Matrices
- **Pin GitHub Actions to commit SHAs (universal modern standard)**: Flag mutable tag references (`uses: dorny/paths-filter@v3`) across all repositories and recommend pinning to a full 40-char commit SHA hash with a version comment (`gh-google-pytorch-torchtpu-vllm-200`).
- **Verify downloaded artifacts & scope GCS globs**: Require cryptographic integrity (`SHA256SUMS`) verification before installing wheels from GCS . Warn against wildcard `*.whl` globs in shared buckets or multi-Python builds where multiple 1GB wheels exist — scope to the exact target Python version and platform, and question using wheels whose test workflow failed.
- **Oldest + Newest dependency slicing & runner capacity**: Test both newest and oldest supported dependency sets  while protecting scarce hardware runner pools. Remove commented-out CI jobs (`gh-google-pytorch-torch_tpu-3630`).

---

## 5. VCS Hygiene, Diffbases, & Commit/PR Descriptions

- **Check commit message accuracy & unrelated diff hunks**: Flag commit messages that reference the wrong tool or stale file/target names (e.g. saying `tox` when the PR updates `nox`), and question any modified `BUILD`, `.bzl`, or C++ header file in the diff that appears unrelated to the PR's stated goal.
- **Flag unwired binary assets & ad-hoc benchmark scripts**: Question checking in binary image/asset files when no HTML `<link>` or docs config references them yet, or checking in untested ad-hoc benchmark shell scripts that get exported to OSS.
- **Split pure refactorings into diffbases**: Ask to split orthogonal refactorings into a parent diffbase PR .
- **Reject low-value automated churn & edits to vendored code**: In OSS repos, push back on automated refactoring PRs (e.g. mass-replacing `yield` loops with `yield from` or editing `_vendor/` files) that add churn without clear semantic value.
- **Scrub copy-pasted boilerplate & stale TODOs**: Flag template comments, commented-out code blocks, duplicate shebangs, and stale TODOs .
- **Substantive `BEGIN_PUBLIC` / `END_PUBLIC` & OSS Changelogs**: Require full motivation inside `BEGIN_PUBLIC`...`END_PUBLIC` on public `torch_tpu` PRs , and `CHANGELOG`/`NEWS.rst` + `AUTHORS`/`Misc/ACKS` in OSS PRs (`gh-pypa-build-168`, `gh-dateutil-dateutil-850`, `gh-python-cpython-134258`).
