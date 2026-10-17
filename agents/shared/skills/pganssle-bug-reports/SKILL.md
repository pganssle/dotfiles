---
name: pganssle-bug-reports
description: >
  How the user (Paul Ganssle) structures and formats bug reports and issues
  filed on other people's projects. Use this whenever you draft, review, or
  reformat a bug report or GitHub/GitLab issue on his behalf. Covers titles,
  reproducers, expected-vs-actual, root-cause, differential findings,
  related-issue linking, and version/platform info. Use the
  pganssle-writing-style skill for the prose voice; see sample-reports.md in
  this directory for annotated exemplars.
---

# Structuring a bug report the way Paul does

A good report lets the maintainer reproduce the problem from a single paste
and understand it without asking follow-ups. Lead with the concrete; explain
only as much as the bug earns.

## Title
- Specific and precise: name the component and the exact symptom, API in
  backticks. E.g. "`datetime.strptime` accepts incompatible arguments";
  "BUG: groupby(..., dropna=False).filter() never includes rows with NaNs in
  the index".
- Follow the project's title conventions when they exist: pandas `BUG:` /
  `REGR:`, an `[FR]` / `[Bug]` tag, etc.
- If it's a regression, mark it (`REGR:`) and say since when if you know.

## Fill the project's template, but keep the substance in the body
If the tracker has a template (repro steps / expected / actual / version,
duplicate-check boxes), fill it honestly. If it's freeform, impose the
structure below yourself.

## Body order (adapt to the bug)
1. **Reproducer first.** Minimal and copy-pasteable: a shell block
   (`mktemp -d`, real commands) or a REPL session with `>>>` and the actual
   output. Prefer an MWE with no dependencies beyond the project itself.
2. **Expected vs actual.** Show the wrong output inline, and state what you
   expected — often as a comment right in the code (`# Expecting: ...`) or an
   explicit "I would want this to show ...".
3. **Root cause, if you found it.** Link the exact source lines with a
   commit-pinned permalink and name the mechanism; for a regression, point at
   the offending commit. If you did *not* confirm it, say so and give a hedged
   best guess.
4. **Differential findings.** Enumerate what does and doesn't trigger it —
   frequently the most useful part for the maintainer.
5. **Way forward.** If there are options, list them and state your lean
   (don't dictate). Flag when something "needs an integration test".
6. **Related issues.** Link them with the relationship explicit and hedged:
   "related to but distinct from #97", "possibly related", "might be a
   duplicate of #99, though...".
7. **Versions / platform.** Exact versions of the project and the relevant
   stack, OS, and language version — at the end, or in the template fields.

## Formatting conventions
- For bug reports and PR descriptions, keep each prose paragraph or list item
  on one physical line and let the hosting platform soft-wrap it. Do not
  hard-wrap prose. Preserve line breaks and indentation inside code blocks.
- Fenced code blocks with language hints (```python, ```toml, ```console).
- Put long tracebacks and logs inside a `<details>` block so the report stays
  scannable.
- Backtick all identifiers, paths, and flags. Use commit-SHA permalinks for
  source references, not branch links (which rot).
- If you learn more after posting, add an "Edit:" addendum rather than
  silently rewriting.

## Calibration
- Keep it as short as the bug allows. Obvious bug → repro plus a sentence or
  two (see attrs #680, dill #411, exchangelib #805). Subtle or design-laden
  bug → the full treatment (cpython #103982, pandas #36948).
- Be honest about what you don't know ("Unfortunately I don't know how I got
  into this state") and about severity ("...but we may as well fix this").
- Anticipate the maintainer's first objection and address it in the report.

Annotated exemplars, grouped by the technique each one demonstrates, are in
`sample-reports.md` next to this file.
