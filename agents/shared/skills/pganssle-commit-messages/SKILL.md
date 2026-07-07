---
name: pganssle-commit-messages
description: >
  Write, edit, or review git commit messages in Paul Ganssle's commit-message
  style. Use when drafting commit subjects or bodies for commits authored by
  Paul, especially alongside pganssle-writing-style, after inspecting a diff,
  staged changes, PR branch, or local git history.
---

# Paul's Commit Messages

Use this with `pganssle-writing-style`. That skill covers Paul's general prose
voice; this one covers the narrower commit-message shape.

## Workflow

Inspect the actual diff before writing the message. Also inspect nearby history
for project-local conventions:

- Keep required prefixes and issue markers, e.g. `GH-103944: ...`,
  `bpo-40503: ...`, `[TorchTPU] ...`.
- Keep repo-generated trailers only when the repo already requires them. Do not
  invent trailers such as `PiperOrigin-RevId`, `Co-authored-by`, or
  `Automerge-Triggered-By`.
- Match the repository's release/changelog idioms for mechanical commits.

Choose the smallest message that explains the change. Many simple commits need
only a subject. Behavioral changes, regressions, compatibility work, and tricky
tests usually need a body.

## Subject

Use a direct, capitalized imperative or short noun phrase:

- `Fix Travis test for pyc files in egg-info`
- `Pin lxml to < 5.2.0`
- `Add failing test for setup_requires`
- `Move build_meta_legacy to build_meta:legacy`
- `Run tests in America/New_York`

Prefer concrete verbs: `Add`, `Fix`, `Remove`, `Move`, `Pin`, `Use`, `Drop`,
`Refactor`, `Update`, `Disable`, `Re-enable`, `Prepare`.

Use scope only when it is naturally part of the repo's history. Avoid generic
summary words like "Improve" unless the change is documentation, cleanup, or
there is no more precise verb.

Do not force Conventional Commits unless the repository already uses them. Do
not add a period to the subject unless the local history does.

## Body Shape

Write in short paragraphs wrapped like a normal git message. The default shape:

1. State the prior behavior, missing invariant, or motivation.
2. Explain what changed and why this approach is reasonable.
3. Mention tests, verification, limitations, or follow-up only when they matter.

Useful openers and transitions:

- `Previously ...`
- `Currently ...`
- `At the moment ...`
- `This adds ...`
- `This fixes ...`
- `This is necessary because ...`
- `This does not address the root issue, but ...`
- `For now ...`
- `Longer term ...`
- `As far as I can tell ...`
- `Apparently ...`
- `Presumably ...`

Explain the "why" more than the "what"; the diff already shows the what. Paul
often records the practical reason a change is acceptable, provisional, or
limited:

- why a pin is acceptable for now
- why a fallback or mitigation is enough to unblock the project
- why a test is intentionally indirect
- why a refactor is split from a move for cleaner history
- why a theoretically possible issue does not matter much in practice

Use bullets or numbered lists when the body is making several independent
claims, enumerating tests, or explaining options. Otherwise prefer paragraphs.

## Calibration

Be precise about certainty. State verified facts plainly, but hedge inferred
causes:

- `It turns out ...` for a discovered cause.
- `Apparently ...` for an observed external behavior.
- `I don't see an obvious or easy way ...` when choosing a pragmatic workaround.
- `This probably does not solve the root issue, but ...` for mitigations.
- `We can revert if it does` for low-risk operational changes.

Do not dramatize. If the change is a workaround, call it a workaround. If it is
temporary, say why it is temporary. If the user-facing behavior does not change,
say that if it helps future readers understand why the commit exists.

## Common Patterns

For a regression fix:

```text
Fix Travis test for pyc files in egg-info

`!` is a special character in YAML syntax, so this was being interpreted
as `grep pyc ...`, not `! grep pyc ...`

I've also added the same `pyc` test to the normal tests.
```

For a dependency pin:

```text
Pin lxml to < 5.2.0

In 5.2.0 lxml apparently dropped their HTML cleaner and moved it to its
own project. We can start depending on the other project later, but for
now we will pin to the last known working value.
```

For a compatibility mitigation:

```text
Limit workers in ProcessPoolExecutor

As a mitigation for #1730, this commit limits the number of workers in
the ProcessPoolExecutor to 1. On PyPy, having a higher number of available
workers dramatically increases the number of concurrent processes, leading
to some resource exhaustion issues.

This does not address the root issue, but should improve the situation
until the root issue is addressed.
```

For a larger technical change, make the invariant and verification explicit:

```text
Add PyTorch-version dispatch for torch_tpu C++ extensions

Introduce the runtime half of the multi-PyTorch-ABI wheel: a MetaPathFinder
installed at import time rewrites imports of `torch_tpu._internal.<module>`
to the glue built for the installed PyTorch version, and an
ExtensionProxyLoader bridges the version-suffixed artifact filename to the
unversioned `PyInit_<module>` symbol the C++ actually exports.

Selection prefers an exact major.minor.patch glue, then the newest patch
built for the same minor. When no versioned glues are bundled, the hook is
not installed and imports resolve normally, so this is a no-op until the
per-version glue build lands.
```

For intentionally separate test commits:

```text
Add failing test for setup_requires

Per GH #1682, with `setuptools.build_meta` we are not properly handling
the situation where `setup_requires` is actually a newline-delimited
string rather than a list, which is supported by the `setup.py` interface.
```

## Avoid

- Do not write marketing copy: no "seamless", "robust", "comprehensive", or
  generic value claims unless the diff specifically justifies them.
- Do not over-structure with headings like "Problem" and "Solution" unless the
  local repo already does that.
- Do not summarize every file touched.
- Do not make the body a PR description if the subject plus one paragraph is
  enough.
- Do not hide uncertainty. Prefer a clear "apparently" or "as far as I can
  tell" to a confident but unsupported root cause.
