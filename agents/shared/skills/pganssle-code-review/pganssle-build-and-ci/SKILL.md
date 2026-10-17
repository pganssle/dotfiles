---
name: pganssle-build-and-ci
description: >-
  Reviews build systems (Bazel, Blaze, BUILD, .bzl, PEP 517/518 pyproject.toml,
  nox/tox), CI/CD workflows (GitHub Actions 40-char commit SHA pinning, GCS
  SHA256SUMS verification, oldest/newest matrices), Copybara configs
  (copy.bara.sky), VCS/PR description hygiene (BEGIN_PUBLIC/END_PUBLIC), and
  documentation/visualization accessibility emulating Paul Ganssle (pganssle).
  Use when reviewing BUILD/.bzl files, GitHub Actions YAML, Copybara configs,
  packaging configs, commit messages, or docs/charts. Don't use for pure Python
  class typing or unit test mock design.
---

# Paul Ganssle (`pganssle`) — Build Hermeticity, CI/CD, Supply Chain, VCS & Docs Hygiene

Review build configurations, CI/CD pipelines, supply-chain security, Copybara rules, VCS commit messages, and documentation/visualization changes with the rigor of Paul Ganssle (`pganssle`).

---

## 1. Build Hermeticity, Bazel & Clean Tool Boundaries

### Bazel Hermeticity & User-Representative Test Environments
- **Fully hermetic builds**: Reject ad-hoc `pip install`, host `/usr/lib` library scraping, or post-build wheel splicing inside shell scripts when Bazel or `nox` should orchestrate the build hermetically (`gh-google-pytorch-torch_tpu-3552`, `gh-google-pytorch-torch_tpu-2353`).
- **Do not mutate library paths or defaults in `build_defs.bzl`**: Do not modify `LD_LIBRARY_PATH` or set non-standard allocator defaults in Bazel test macros in ways that diverge from how real users run the package — tests should run as if we were a user.
- **internal_repo `BUILD` hygiene (`exports_files` & `pytype_strict_library`)**:
  - Flag `exports_files([...])` blocks that export internal `.py` module or test files which no other package should consume directly as raw source files.
  - Prefer `pytype_strict_library` (from `//tools/build_defs/python:pytype.bzl`) over raw `py_library`.
- **Single responsibility for scripts & test files**: Do not bury unrelated environment setup inside a script dedicated to running `bazel-diff`, or put unrelated tests inside a narrow test module .
- **Explicit CLI flags & scheduler-friendly lifecycles**: Prefer explicit CLI flags over ambient env vars , file-path flags over raw JSON strings (`gh-google-ml-infra-bap-23`), and letting external cron schedulers manage intervals rather than `time.sleep(interval)` at the end of `main` .

---

## 2. CI/CD Workflows, Formatters, Copybara & Supply Chain Security

### Linter Workflows & Formatter / Copybara Interaction
- **Consolidate linter workflows**: Prefer adding a job or step to an existing `lint.yml` workflow (named accurately, e.g. `"Run code linters"` rather than `"formatting"`) over proliferating separate `.github/workflows/*.yml` files (`gh-google-pytorch-torch_tpu-3443`).
- **Copybara `pyformat` vs. external formatters (`ruff format`)**: In internal_repo repositories exported via Copybara (`torch_tpu`), remember that Copybara automatically formats code with `pyformat` on import and export. Question enabling `ruff format` in CI unless it is verified to produce identical output to `pyformat`, and note that running a file-level formatter on modified files in CI will reformat untouched lines in those files.
- **Clean `pyproject.toml` & `.bzl` formatting**: Flag commented-out config lines or unused tool sections (such as `[tool.ruff.lint.isort]` when import sorting isn't enabled) in `pyproject.toml`, and question generated `.bzl` files that are collapsed onto a single giant unformatted line or repetitive target blocks that can be generated with a loop.
- **Copybara configuration (`copy.bara.sky`)**:
  - Question removing `patching_enabled = False` (when the package carries no patches), removing test files (`conftest.py`) from `git_files`, or removing `version_selector` semver rules.
  - When `noop_behavior = "IGNORE_NOOP"` is used on a `core.transform` block to stage a migration, ask to add a `TODO` to remove the `IGNORE_NOOP` (*"We should add a TODO to remove the IGNORE_NOOP."*).
  - Prefer `.patch` files (`patch.apply`) over large multi-line `core.replace` blocks.

### Supply Chain Security, Artifact Globs & CI Matrices
- **Pin GitHub Actions to commit SHAs (universal modern standard)**: Flag mutable tag references (`uses: dorny/paths-filter@v3`) across all repositories and recommend pinning to a full 40-char commit SHA hash with a version comment (`gh-google-pytorch-torchtpu-vllm-200`).
- **Verify downloaded artifacts & scope GCS globs**: Require cryptographic integrity (`SHA256SUMS`) verification before installing wheels from GCS . Warn against wildcard `*.whl` globs in shared buckets or multi-Python builds where multiple 1GB wheels exist — scope to the exact target Python version and platform, and question using wheels whose test workflow failed.
- **Oldest + Newest dependency slicing & runner capacity**: Test both newest and oldest supported dependency sets  while protecting scarce hardware runner pools. Remove commented-out CI jobs (`gh-google-pytorch-torch_tpu-3630`).

---

## 3. VCS Hygiene, Diffbases, & Commit/PR Descriptions

- **Check commit message accuracy & unrelated diff hunks**: Always cross-check whether the PR/PR title and description claim a different tool, file name, or test target than the diff actually implements (e.g. saying `tox` when the PR updates `noxfile.py`, or referencing stale file/target names), and question any modified `BUILD`, `.bzl`, or C++ header file in the diff that appears unrelated to the PR's stated goal.
- **Flag unwired binary assets & ad-hoc benchmark scripts**: Question checking in binary image/asset files when no HTML `<link>` or docs config references them yet, or checking in untested ad-hoc benchmark shell scripts that get exported to OSS.
- **Split pure refactorings into diffbases**: Ask to split orthogonal refactorings into a parent diffbase PR .
- **Reject low-value automated churn & edits to vendored code**: In OSS repos, push back on automated refactoring PRs (e.g. mass-replacing `yield` loops with `yield from` or editing `_vendor/` files) that add churn without clear semantic value.
- **Scrub copy-pasted boilerplate & stale TODOs**: Flag template comments, commented-out code blocks, duplicate shebangs, and stale TODOs .
- **Substantive `BEGIN_PUBLIC` / `END_PUBLIC` & OSS Changelogs**: Require full motivation inside `BEGIN_PUBLIC`...`END_PUBLIC` on public `torch_tpu` PRs , and `CHANGELOG`/`NEWS.rst` + `AUTHORS`/`Misc/ACKS` in OSS PRs (`gh-pypa-build-168`, `gh-dateutil-dateutil-850`, `gh-python-cpython-134258`).

---

## 4. Documentation, Visualization Accessibility & Precision

- Require inline comments explaining *why* for `# type: ignore` / mypy workarounds (with issue link), private stdlib imports (`# pylint: disable=protected-access`), custom file-reading wrappers (`with open(path)`), or subtle header directives.
- Check docstrings and embedded SQL/prompt templates for **placeholder table/variable name consistency** (`MyInputTable` vs `input_table`), exact semantics (`"maximum number of responses"` vs `"number of responses"`), and docstring-to-implementation consistency (e.g., `jobs <= 0` auto-detection).
- In plotting/visualization code, flag red/green palettes (`#EA4335` / `#34A853`) and recommend colorblind-safe palettes (blue/orange or Okabe-Ito).
- In Markdown/HTML docs adding inline logos/images, check vertical alignment, relative height units (`height="1em"` or `1rem`), and unnecessary `&nbsp;`.

---

## 5. Voice & Framing Reference

Follow [references/voice-and-examples.md](references/voice-and-examples.md) when formatting review comments.
