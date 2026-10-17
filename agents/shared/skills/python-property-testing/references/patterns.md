# Patterns and sources

## Choose the right notion of equivalence

- `dateutil/tests/property/test_isoparse_prop.py`: an ISO round trip preserves
  wall time and offset. Named zones and parsed fixed offsets need not compare
  equal at ambiguous times under PEP 495. Assert retained information instead of
  excluding those times.
- `zoneinfo/tests/test_zoneinfo_property.py`: pickle properties distinguish
  cached identity from fresh `no_cache` objects. C/Python comparisons check
  successful results and require conversion overflow to occur consistently.
- `audio_feeder/tests/test_segmenter.py`: compare an optimized algorithm with
  exhaustive search on short lists. Compare optimal scores, since different
  segmentations can tie; use cheaper properties for larger inputs.
- `pytz-deprecation-shim/tests/test_pytz_equivalent.py`: historical data and offset
  precision limit a differential oracle. Document those limits without treating
  them as restrictions on the target's own contract.

These are examples of test design, not templates for historical coding style.

## Test parser behavior beyond formatter output

Formatters often emit only canonical padding or precision. Generate accepted
alternatives directly, and test invalid inputs by corrupting one field of a valid
case. Separate properties for representations, precision, errors, and environment
changes make failures easier to interpret.

Distinguish input acceptance from output consistency. For example,
`time.strptime("2016 52 0", "%Y %W %w")` has returned January 1, 2017 with
`tm_yday=367`. Whether overflowing week representations should be accepted is
separate from whether the resulting date fields should agree. Read the current
discussion in [CPython #73267](https://github.com/python/cpython/issues/73267)
before treating either expectation as settled.

For date/time tests, consider leap centuries, week/year boundaries, fold/gap
transitions, precision, and extrema. Compute UTC bounds in UTC. Decide explicitly
whether each assertion concerns wall time, instant, offset, fold, or identity.

## Primary sources

- [Hypothesis: domain and distribution](https://hypothesis.readthedocs.io/en/latest/explanation/domain.html):
  preserve the valid domain while tuning search effort.
- [Custom strategies](https://hypothesis.readthedocs.io/en/latest/tutorial/custom-strategies.html)
  and [strategy reference](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html):
  construct dependent inputs and retain useful shrinking.
- [Hypothesis API](https://hypothesis.readthedocs.io/en/latest/reference/api.html):
  explicit examples, `.xfail()`, reproduction, settings, and health checks.
- [Fixture lifetimes](https://hypothesis.works/articles/hypothesis-pytest-fixtures/)
  and [stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html):
  isolate examples; generate action sequences when history matters.
- [LLVM fuzz targets](https://llvm.org/docs/LibFuzzer.html#fuzz-target) and
  [corpora](https://llvm.org/docs/LibFuzzer.html#corpus): keep targets focused,
  deterministic, and fast; retain useful inputs for replay.
