# Sample bug reports (Paul Ganssle) — annotated exemplars

A curated set of the user's own issues on *other people's* projects, chosen to
show the range and the recurring techniques. Read a couple before drafting.
(His `pganssle/*` and `dateutil/*` repos are excluded — those are his own
project management, not reports to third parties. BPO-migrated CPython issues
like #86826 and #90772 are also excluded: their bodies are auto-generated
migration tables, not his prose.)

## Tight library bugs — minimal repro, inline expected output
- **pandas #44517** — `groupby(..., dropna=False).filter()` drops NaN groups.
  https://github.com/pandas-dev/pandas/issues/44517
  The template: dependency-free repro, expected output written as a comment in
  the same code block, one-line "Expected Behavior". This is the baseline shape.
- **attrs #680** — slots class overrides custom `__setattr__` in 20.1.0.
  https://github.com/python-attrs/attrs/issues/680
  How short a good report can be: before/after REPL snippets, one sentence of
  framing, "When `slots=False`, the same thing does not occur" as the differential.
- **dill #411** — dill fails to pickle attrs classes.
  https://github.com/uqfoundation/dill/issues/411
  MWE that contrasts working (`pickle.dumps`) vs failing (`dill.dumps`);
  traceback tucked in a `<details>`.

## Shell / tool bugs with differential diagnosis
- **astral-sh/uv #12173** — `venv` broken via a symlink to a uv-installed Python.
  https://github.com/astral-sh/uv/issues/12173
  Copy-pasteable `mktemp -d` repro; "full path works... pyenv works too, so this
  seems uv-specific"; hedged links to possibly-related issues.
- **pylint #3866** — false-positive unused-variable in a lambda with `*args`.
  https://github.com/pylint-dev/pylint/issues/3866
  The differential-diagnosis showcase: enumerated list of what does and doesn't
  trigger it, a single minimal file covering all cases, and the aside "I'm not
  entirely shocked... this hasn't been reported before".

## Root-caused bugs — cite the exact line / commit
- **pandas #36948** — REGR: `DataFrame.agg` no longer accepts positional args.
  https://github.com/pandas-dev/pandas/issues/36948
  `REGR:` title, offending commit identified, the exact `axis`-passed-twice
  mechanism explained, and the fix proposed ("pass `axis` by position").
- **cpython #91581** — unchecked error in `_datetimemodule.c` on `fromtimestamp` > Y10k.
  https://github.com/python/cpython/issues/91581
  Traces to a specific `utc_to_seconds` call (permalinked), then honestly
  down-calibrates: "as a practical matter... but we may as well fix this".
- **pypa/build #98** — missing-backend error when PEP 518 reqs aren't satisfied.
  https://github.com/pypa/build/issues/98
  Repro + source-line root cause + "related to but distinct from #97" +
  "I think this definitely needs an integration test".

## Design-laden bugs — enumerate options, state a lean
- **cpython #103982** — `astimezone(None)` does not set `fold`.
  https://github.com/python/cpython/issues/103982
  Real-world origin ("At work today someone presented this problem"), careful
  conceptual walkthrough, three enumerated ways forward with "I'm leaning
  towards starting with 1", and "@abalkin Any thoughts on this?".
- **cpython #124549** — `datetime.strptime` accepts incompatible arguments.
  https://github.com/python/cpython/issues/124549
  Presents a bug whose *fix* is debatable: raises the ban-it option, argues
  against it, lists alternatives including "just accept weird behavior".

## Investigative / log-heavy, cause unknown
- **koreader-calibre-plugin #115** — sync fails on UUID mismatch.
  https://github.com/kyxap/koreader-calibre-plugin/issues/115
  Pastes debug logs, reasons about which data source is wrong, honest
  "Unfortunately I don't know how I got into this state", enumerated expectations.
- **ankidroid #15911** — localStorage not persistent.
  https://github.com/ankidroid/Anki-Android/issues/15911
  Full template filled well: stepwise repro, expected vs actual, real-world
  motivation, links another user hitting the same thing.

## Compatibility / heads-up reports
- **exchangelib #805** (and the parallel maya #191, clickhouse-driver #166) —
  incoming `tzlocal` change will break the package.
  https://github.com/ecederstrand/exchangelib/issues/805
  Short, actionable, points at the upstream change, offers the short-term pin
  and the long-term migration path (with his shim linked).

## Proposals / feature requests (voice, less about bug structure)
- **cpython #103857** — deprecate `utcnow` / `utcfromtimestamp`.
  https://github.com/python/cpython/issues/103857
  "Pitch" + "Previous discussion", links his own articles, and openly narrates
  changing his own mind ("I have come around to the idea that...").
- **cpython #91928** — add `datetime.UTC` alias.
  https://github.com/python/cpython/issues/91928
  Small QoL proposal, honestly scoped ("This isn't a *huge* deal, but...").
