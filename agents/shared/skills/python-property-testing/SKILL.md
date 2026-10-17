---
name: python-property-testing
description: >
  Write, extend, or review Hypothesis property tests.
  Use for choosing meaningful properties and strategies, investigating generated
  failures, preserving explicit regression examples, and balancing discovery
  with CI cost. Complements python-testing and python-coding; also applies when
  designing assertions and input domains for Python fuzz targets.
---

# Property testing with Hypothesis

Use [python-testing](../python_testing/SKILL.md) and
[python-coding](../python_coding/SKILL.md) for the general conventions. Keep
their public-interface focus, type hints, module imports, and fixture preference.
Respect the project's supported Python versions and test framework. Older tests
are evidence about useful properties, not a reason to copy obsolete syntax,
private-interface assertions, or inheritance into a new pytest suite.

Use property tests to discover bugs and unclear contracts as well as to
prevent regressions. A passing suite isn't sufficient if getting there meant
discarding cases that should work. Preserve discoveries as explicit examples,
and make the property understandable without having to decode its generator.

For concrete patterns and their provenance, read
[references/patterns.md](references/patterns.md) when choosing an oracle,
working on dates or parsers, or deciding how to handle a surprising failure.

## Choose the assertion before the strategy

State the public behavior, its preconditions, and what observation would falsify
it. Prefer focused tests with descriptive names over one large property with
many unrelated branches. Several assertions can describe one coherent contract.
Keep independently useful additions separable; when the requested workflow calls
for commits, one focused property per commit makes review and removal easier.

Choose an oracle appropriate to the contract:

- **Round trips:** identify precisely what survives serialization. Check the
  retained fields, precision, offset, or canonical representation. A lossy format
  doesn't promise object equality, and accepting a string doesn't imply a
  formatter can reproduce it verbatim. Supplement inverse checks where both
  directions could share a bug.
- **Differential checks:** compare public behavior of C/Python implementations,
  entry points, or a trusted reference on their shared contract. Compare exception
  behavior as well as successful results. Agreement alone doesn't prove either
  implementation correct; disagreement isn't automatically a bug in the target.
- **Simple models:** use an independent, obviously correct algorithm, including
  brute force on small inputs. Compare the promised objective or equivalence
  class if several outputs are valid, rather than imposing one arbitrary answer.
- **Metamorphic relations and invariants:** test a justified relationship under
  a transformation: idempotent normalization, equivalent representations,
  preserved contents, or invariance under an allowed reordering. Don't assume
  order independence when precedence is part of the API.
- **Error contracts:** generate known-invalid cases and assert the documented
  exception. A robustness test over arbitrary inputs may allow specific expected
  errors, but must expose unexpected ones. Don't catch every exception.

A no-crash property can be useful, but add semantic assertions when the public
contract gives you something stronger to check. Coverage helps locate gaps; it
doesn't establish that the assertions would detect wrong results.

## Generate interesting cases without excluding surprises

Use domain strategies such as dates, times, and timedeltas instead of assembling
mostly-invalid primitive tuples. Build dependent values together with strategy
composition or `@composite`; generate a valid object and its representation when
that makes the relation explicit. Keep the oracle independent of the code under
test rather than reproducing its algorithm in a strategy.

Start with the full domain where the property should hold. Use focused domains
to guarantee useful scenarios, while retaining broad coverage where practical.
For invalid-input properties, corrupt one field of an otherwise valid input so
the expected rejection has a clear cause. Arbitrary bytes or text are a separate
way to probe unexpected errors; they won't efficiently cover every valid grammar.

Use `assume()` or `.filter()` for genuine preconditions when construction would
be awkward and rejection is modest. Explain non-obvious exclusions. Never turn
a newly discovered failure into an assumption merely to get a green run.
Performance bounds and reference-implementation limitations need an explicit
reason; they don't redefine the target's supported inputs. Where feasible, cover
the excluded valid region with a different property or a tracked regression.

Make shrinking useful: prefer simple data shapes and stable ordering for
`sampled_from` values. Put simpler representative cases before special variants
when their order affects shrinking. Don't introduce untracked randomness or draw
inputs with `strategy.example()` inside tests. Use keyword arguments for readable
`@given` and `@example` cases, following the surrounding suite's conventions.

Add deliberate examples around boundaries and semantic transitions: empty and
minimal values, extrema, just inside/outside limits, precision changes, ambiguous
representations, and interactions between fields. Select cases for distinct
behavior, not just large quantities of arbitrary examples.

## Treat a failure as a finding to investigate

Reproduce and shrink it, then distinguish a product bug from a false property,
a generator mistake, an environment limitation, or an unresolved contract.
Consult documentation and existing issues when the expectation is uncertain.
Other languages and implementations provide evidence, not authority over this
API. An open issue can contain a working-as-intended conclusion; read the
discussion before describing something as a confirmed bug.

For useful counterexamples, add a concrete `@example` to the relevant property
with a short explanation of what it exercises. A Hypothesis database, seed, or
failure blob is useful for reproduction, but isn't a substitute for a maintained
regression example. Explicit values must exercise the same semantic path as the
generated inputs, including awareness, units, and environment assumptions.

Keep the intended assertion for valid behavior that currently fails. If a fix is
outside the task, isolate the known failure in a narrow regression/property and
use the project's expected-failure mechanism with a reason and canonical issue
reference when available. Prefer strict unexpected-pass reporting. Don't mark a
broad passing property expected to fail: an unrelated error could then look like
the known bug. Restrict expected exception types where the mechanism supports it.

`@example(...).xfail(...)` affects only that explicit case; generated occurrences
of the same bug still fail. Don't silently filter those occurrences out. A
separate focused
expected-failure test can preserve the failing region while other properties
continue to discover unrelated bugs.

Record findings in the task's notes or report: minimal input, actual and expected
behavior, the basis for the expectation, affected versions/platforms, and related
issues or PRs. Label disputed behavior and documentation questions honestly.
Don't file issues or modify PRs unless the user has authorized that action.

## Separate discovery effort from routine CI cost

Measure the focused suite. Use the project's settings/profiles to keep routine
runs inexpensive and permit larger local or scheduled discovery runs. Budget
for parameter combinations, implementations, and costly setup as well as example
count. `max_examples` isn't a hard bound on total calls or elapsed time.

Prefer reducing routine search effort before excluding valid values. Bound an
expensive oracle's input size when justified, and supplement it with cheap
properties over larger inputs. Don't add huge Cartesian products or long fuzzing
runs to every CI job by default. Investigate health checks and deadlines; adjust
them deliberately rather than suppressing warnings wholesale.

Check how the repository actually runs property tests. If it has a shim that
executes `@example`s without Hypothesis, give each property meaningful examples
covering its important branches. When a useful feature is missing from the shim,
prefer extending the shim over weakening the test or foregoing that feature.
This includes `@example(...).xfail(...)`: preserve expected failures, exception
matching, and unexpected-pass reporting in both modes. Add focused tests for new
shim behavior, checking it against the supported Hypothesis API. A shim should
replay explicit examples faithfully; it needn't implement random generation.
Verify both real generation and shim execution, including collection and expected
failures. A shim-only pass verifies examples, not generation.
This is a CPython workflow to support where present, not a requirement to build
shims or remove Hypothesis from other projects' CI.

Keep each generated case reproducible and isolated. Pytest function fixtures and
unittest setup don't reset for every Hypothesis example; create or reset mutable
state inside the example when needed. Restore locale, time zone, caches, and
module replacements using the project's supported test facilities. Reuse
expensive immutable data where appropriate, with stable ordering.

For operation sequences, use a stateful model when the bug depends on history
rather than a single value. For fuzz targets, keep the target focused, fast, and
deterministic, preserve minimized failure inputs, and catch only errors allowed
by the contract. Use the project's existing fuzzing infrastructure rather than
adding a new engine as a side effect of writing a property test.

Report which modes and implementations ran, measured cost, retained examples,
and unresolved findings. A large generated run supplies evidence, not a proof
that the property holds everywhere.
