---
name: consensus-build-and-ci
description: >-
  Writes and updates Bazel/BUILD files, Python packaging (pyproject.toml, flit,
  tox, uv, modern native backends), GitHub Actions workflows, documentation,
  changelogs, and commit messages to satisfy pganssle, wan, and pablogsal.
  Covers hermetic builds, 40-char Action SHA pinning with automated updates,
  SHA256 verification, stale-reference sweeps, and user-facing docs. Use
  whenever editing build, CI, packaging, or doc files.
---

# Consensus Build, Packaging, CI & Docs (`pganssle` + `wan` + `pablogsal`)

Keep builds hermetic, supply chains pinned and automatically updated, packaging clean and modern, and documentation aligned with what users actually observe.

## 1. Bazel / `BUILD` & `.bzl` Hygiene

- **Strict hermeticity**: Never scrape host paths like `/usr/lib`, mutate `LD_LIBRARY_PATH` inside `.bzl` rules, or download unpinned network artifacts during build steps.
- **Target precision**:
  - Use strict typed library rules (`pytype_strict_library` where supported) and mark test helpers/fakes `testonly = True`.
  - Never list the same `.cc` source file in both a library `deps` target and a binary/test `srcs` list (causes duplicate compilation and ODR bugs).
  - Never write broad `exports_files(glob(["**"]))`; export only the exact files needed across packages.
  - Remove unused `deps` entries and delete orphaned `.diff` / patch files whenever upgrading or refactoring dependencies.
  - Declare runtime files in `data = [...]` so `bazel run` and `bazel test` find them hermetically.
- **Naming, sorting & generated blocks**:
  - Use `snake_case` for target names and source files; give `.bzl` files distinct names across directories.
  - Apply test filter tags (`notap`, `notest_oss`, `manual`) according to their exact runner semantics.
  - Keep target and `deps` lists sorted (`# keep-sorted`).
  - Above every generated section in a `BUILD` or config file, include the exact copy-pasteable command that regenerates it.
- **Protect local build speed**: Scope heavy sandboxing or remote-only flags (`--spawn_strategy=sandboxed`) under `--config=ci` in `.bazelrc`, not unconditional local defaults.
- **Single-source toolchain pins**: Keep upstream commit hashes (such as `.torch_commit`) in a single file with a `# YYYY-MM-DD` comment and step-by-step update instructions.

## 2. Python Packaging (`pyproject.toml`, `flit`, `tox`, `uv`)

- **Pure-Python libraries** (`pganssle` default):
  - Default to `flit_core.buildapi` (`flit`) because it is the simplest standard backend. Use a static `version = "X.Y.Z"`, `readme = "README.md"`, and `license = {text = "Apache-2.0"}`.
  - Avoid `setup.py` whenever possible.
  - Separate runtime `dependencies` from test and lint dependencies (`[dependency-groups]` or `[project.optional-dependencies]`).
- **Compiled C / C++ / Rust extensions**:
  - Choose a modern standard PEP 517 build backend on a case-by-case basis (such as `meson-python`, `hatch`, `scikit-build-core`, `maturin`, or `bazel`).
  - Do not introduce `setup.py` in new projects. Only touch `setup.py` + `CMakeLists.txt` parity when maintaining an existing repo that already uses both.
- **Isolated test & dev environments**:
  - Use `tox` for matrix testing and `nox` (with temporary virtualenvs) or `uv run` for repository helper scripts.
  - Never run `pip install` into the host/system Python environment from a repo script.
- **Standalone scripts**:
  - Add `# /// script` (PEP 723) inline metadata at the top of standalone scripts that need third-party packages.

## 3. GitHub Actions & Supply Chain Security

- **Pin actions to 40-char SHAs** (`zizmor` / `pganssle` standard): Pin every third-party `uses:` line to its full 40-character commit SHA followed by a version comment:
  ```yaml
  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
  ```
- **Keep pinned SHAs updated automatically**:
  - Ensure the repository has automated SHA updates configured (for example, `.github/dependabot.yml` with `package-ecosystem: "github-actions"` or Renovate).
  - If automated updates are not yet set up in the repository and adding them is out of scope for the current PR, add a `# TODO:` comment in the workflow noting that Dependabot or Renovate should be enabled to keep the pinned SHAs up to date.
- **Verify downloaded artifacts**: Check `SHA256SUMS` before executing or unpacking downloaded archives, and scope `*.whl` / `dist/*` globs tightly so stray build files cannot be uploaded.
- **Workflow organization**:
  - Group fast static checks (`ruff`, `mypy`, `codespell`, `zizmor`) into a single `lint.yml` workflow rather than spawning many separate workflows.
  - Never hardcode repository owner/name or default branch strings inside workflow YAML; use `${{ github.repository }}` and `${{ github.ref_name }}`.
  - Test against both the oldest supported minimum dependency versions and the latest releases.
- **Respect repository formatters**: Do not introduce `ruff format` or `black` into a repository managed by Copybara or an existing canonical formatter.

## 4. Documentation, Changelogs & Removals

- **Stale-reference sweep on every deletion**: After deleting any symbol, CLI flag, config key, file, or workflow step, search the entire repository (source, tests, `BUILD`, CI YAML, `README.md`, docs) and clean up every remaining reference.
- **Explain removed checks or caches**: Never silently delete a cache, fast path, guard check, or CI job. Document why it is no longer needed and provide before/after benchmark numbers when performance is involved.
- **User-facing changelogs (`NEWS` / `CHANGELOG.md`)**: Write entries from the user's point of view, referencing public module and function names (`:mod:` / `:func:`), never private `_` implementation helpers.
- **Keep `README.md` user-facing**: Put maintainer release steps and internal architecture notes in `MAINTENANCE.md` or `CONTRIBUTING.md`, while keeping user-visible platform support and known limitations in `README.md`.
- **Cross-link discoverably**: Link new docs or caveats from the main API docstring or index page where users look first.
- **Accessible diagrams & badges**: Use colorblind-safe palettes (blue/orange or Okabe-Ito, never red vs. green alone) and relative image heights (`1em` / `1rem`) for inline icons.

## 5. Commit Messages & Version Control

- **Match the final diff**: Update commit titles and descriptions whenever code changes during iteration so they accurately name the tools, flags, and targets in the final patch.
- **Lead with *why***: Explain the problem and motivation in the commit body (including inside `BEGIN_PUBLIC` / `END_PUBLIC` sections when applicable).
- **Never add `SKIP_COPYBARA`**: Never include `SKIP_COPYBARA` tags in commit or changelist descriptions.

## Quick Checklist Before Finishing Build, CI & Docs
- [ ] `BUILD` / `.bzl` rules are hermetic, sorted, free of duplicate `srcs`+`deps`, and declare runtime `data`.
- [ ] Pure-Python packaging uses `flit`; compiled backends avoid `setup.py` in favor of modern PEP 517 backends or `bazel`.
- [ ] GitHub Actions `uses:` lines are pinned to 40-char SHAs with `# vX.Y.Z` comments, plus Dependabot/Renovate automation (or a `TODO` to add it).
- [ ] Every deleted symbol, flag, or file has zero stale references left in code, build files, CI, or docs.
- [ ] Changelogs and `README.md` describe user-visible behavior; commit messages match the final code and omit `SKIP_COPYBARA`.
