# API Surface, Error Ergonomics, Grammar-as-API & Scope Discipline (`pablogsal`) — Pass 2 Reference (v5)

> **v5**: the clarity & micro-contract checklist runs on **every** modified hunk (not only silent ones; Python/Cython with the same weight as C/C++); layout/size hunks, the armed-feature counterfactual and `exec`-plus-value on compile-only tests are Tier 1 ledger items; fallible accessors get a direct `NULL`-check request (no macro alternative); eight more positive facts in [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md).

> **v4 rules**: three-way gate — proven in the diff → emit (fence for one-liners); author intent genuinely open → ask with the assumption stated; a general runtime/language/library/tooling contract or anything the diff contradicts → **do not post, not even as a question** (consult [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md)); mandatory second-look pass over every hunk that produced no comment (name-vs-body, declaration locality, regex readability, point-of-reliance comments, unchecked accessors ticked without reachability reasoning, consumer-side accumulator overflow, tooling rationale); fences compiled against the whole scope; comments on unchanged or verbatim-moved lines dropped.

> **v3 rules**: no comment budget (every proven finding, every repeated-pattern anchor as its own one-line comment, and the central design objection are always emitted); proof by quotation before any bug/leak/crash/"cannot fail" claim, with `major`/`blocker` requiring a quoted diff line and assumption-dependent claims downgraded to `question`/`minor`; a stale-reference search after every deletion; every one-line change ships a ```` ```suggestion ```` fence; content nits (typos, stray `>>>` prompts, wrong example output) are posted, not deleted as formatting.

Condensed single-skill fallback for [`pablogsal-api-design`](../pablogsal-api-design/SKILL.md). All rules are grounded in `train_reference_public.jsonl` and `writings_and_talks_public.jsonl` (ids in parentheses).

---

## 0. v2 additions: deletions, user input, doc-vs-code, discoverability, heuristics
- **Every removed option/flag/check/warning/doc section/public symbol is a question**: *"Why do we need to drop this? … no?"*; on perf/observability paths add the cost model and ask for data (*"not a blocker, but let's measure before landing so we know what we are trading"*); when a whole workflow changes, ask the author to explain and document it.
- **User input**: enumerate what users will type (spaces, case, abbreviations, units) against any regex/parser; the error message must state the accepted syntax; `re.VERBOSE` + sample inputs for anything longer than a few tokens (`gh-bloomberg-pystack-206`).
- **Doc vs code**: when they disagree about a default/behaviour, **ask which is intended** and propose the doc fix; never assert a regression or flip the code default.
- **Discoverability**: when documentation lands in one place, ask where a user would look first and whether that place cross-references it (`gh-python-cpython-96445`).
- **Heuristics**: enumerate tokens ambiguous between unary and binary use in soft-keyword/operator lists; prefer the rule that cannot mis-classify valid input.
- **Refactor-hidden behaviour change**: construct an input where old and new differ, say which is right, ask for a test per affected surface. **Ask, don't narrate**: *"Can you comment a bit on why we need this line?"*
- **Verification before assertion**: process facts (`Patch by …` is the standard credit; ACKS is self-service; NEWS sections follow the changed file) come from [era-api-timeline.md](era-api-timeline.md) §3, never from memory; state release-status assumptions before asking for deprecation aliases or NEWS entries.

## 1. The Compiler and the Traceback Are User Interfaces
- A specialised `SyntaxError` rule is a bug if it is wrong for **any** valid program; test the counter-examples (`print((yield 1), x=2)`, `[lambda: (yield x) for x in xs]`) before accepting it (`gh-python-cpython-157767`).
- Prefer the coarser always-correct location: *"I’d prefer a shorter underline over another version of yield parsing we need to maintain."*
- One rule → one error; split *"missing operand after `yield from`"* from *"missing parentheses"*.
- No enumerated operator/follow-token lists (*"another place to keep in sync with the expression grammar"*); never modify a working rule to attach an `invalid_*` alternative (*"Why are we changing this rule?"*, `gh-python-cpython-123629`); ask why a rule matches `disjunction`/`expression_without_invalid` (*"Isn't that too generic?"*, `gh-python-cpython-133851`).
- Reject NUL bytes in the tokenizer so `compile()` and file parsing agree (`gh-python-cpython-97577`).
- Tracebacks must not hide the argument that caused the failure; a wrong `end_lineno` is a compiler bug, not a formatting bug (`gh-python-cpython-112097`).
- PEP 657 contract: `-1` in C, `None` in Python; `uint8_t` storage is an implementation detail that can be lifted later (`gh-python-peps-2022`).

## 2. Compatibility, Protocols & Symmetry
- Never change a callback protocol's arity; feature-detect extensions — the `readline` completer is `(text, state)` and a 3-arg call *"will raise `TypeError` here, which we swallow … and silently return no completions"* (`gh-python-cpython-122380`).
- Internal component names stay out of public headers (`pegen_interface.h` → `parser_interface.h`, `gh-python-cpython-21016`).
- Keep helper families symmetric (`PyInterpreterState *interp` everywhere) *"That way the code of the caller will be also cleaner"* (`gh-python-cpython-113584`).
- Deprecated names are API debt (`tp_del` → `tp_finalize`, `gh-python-cpython-27165`).
- Parameter names are API unless positional-only (`pep-0570`); explicit opt-in syntax beats ambient switches (`pep-0810`); attractive nuisances earn compiler warnings (`pep-0679`); bare `except:` swallows `KeyboardInterrupt` (`pep-0760`); judge by downstream stability (`talk-pycon-taiwan-2023-theseus`).

## 3. Failure Semantics
- Validate the whole input before committing side effects so the caller can recover (*"Should we walk and validate the whole structure first so this is all-or-nothing?"*, `gh-python-cpython-157228`).
- Do not claim safety you cannot prove: strong references or re-read sizes around anything that can run `__index__`/`__hash__`; otherwise *"let's not close the issue with this PR."*
- Custom exceptions in `errors.py`, rendered centrally in `__main__`; `sys.exit` already raises; no gigantic `try` bodies (`gh-python-cpython-142655`).
- Unsupported combinations raise `NotImplementedError` and are tested; constructor-time rejection of incompatible options is asked as a question (*"🤷 WDYT?"*, `gh-bloomberg-memray-277`).
- Print before `abort()`; log failed `close()` (`gh-bloomberg-memray-277`, `gh-bloomberg-pystack-126`).

## 4. CLI & Configuration
- Flag conflicts as a table (`incompatible_flags = {args.force: "--force", …}`) with one `parser.error` (`gh-bloomberg-memray-458`).
- Clear operator errors (unknown PID) through the central path; smoke tests per option.
- No hard-coded repository/branch values in workflows (*"I don't like all these hardcoded values"*, `gh-python-peps-1996`).
- Dependencies are API: test-only deps imported at runtime (`gh-y-crdt-pycrdt-356`); optional imports during collection change what unrelated code exercises (`gh-bloomberg-memray-1033`).

## 5. Naming & Documentation Precision
- Names say exactly what the code does: `setMainTidAndSkipFrames`, `skip_last_contribution`, not `_dedented_lines` for something that also strips (`gh-bloomberg-memray-209`, `-326`, `gh-python-cpython-112097`).
- Docs state real semantics (*"all leading whitespace characters"*, `gh-python-cpython-22469`); separate public API from implementation detail in PEP prose; add *"and they will remain self-contained"* where copyability matters (`gh-python-peps-2022`, `-1695`).
- Readability edits via `suggestion`: typos, a comma, bullets, a HOWTO link (`gh-python-peps-1359`, `gh-python-cpython-96445`).
- Comments explain the *recipe*/*example*/*provenance*, not the obvious (`gh-bloomberg-memray-317`, `gh-python-cpython-112097`).
- README is for users; maintainer notes go to `MAINTENANCE.md` (`gh-bloomberg-pytest-memray-20`).

## 6. Scope Discipline
- *"Can we drop this rule for now?"* · *"I’d leave slices out of this PR."* · *"Let's keep this one focused on container validation."* · *"Happy to take this as a follow-up, but then let's not close the issue with this PR."* · *"Can you revert the header change so the diff stays minimal for the backport?"* (`gh-python-cpython-157767`, `-157228`, `-157732`)
- Ask *"Why was this just moved over here?"* / *"Is this needed for the fix?"* for hunks the title does not explain.
- Withdraw when *"the benefits doesn’t justify the cost"* (`discourse-pep760-bare-excepts`).

## 7. Era Calibration
| Era | Watch for | Never demand |
| :--- | :--- | :--- |
| 2018–2021 CPython 3.7–3.10 | header/API leakage, PEP wording, `literal_eval` semantics | `gh-` refs, `PyUnstable_*` |
| 2022–2023 CPython 3.11/3.12 · Memray/PyStack CLIs | `perf` doc links, `attach`/`FileFormat` contracts, README placement | Click/Rich migrations |
| 2024 CPython 3.13 | grammar-rule stability, `_pyrepl` exit codes, freelist API symmetry | breaking `readline` protocol |
| 2025–2026 CPython 3.14/3.15 | `profiling.sampling` errors, writer safety claims, completer arity, NEWS accuracy | ambient switches, partial fixes closing issues |

## 8. Annotated Mini-Examples
1. **`gh-python-cpython-157767`** — *"Can we drop this rule for now? I don’t like having another list of all the operators just for this error. It’s another place to keep in sync with the expression grammar."*
2. **`gh-python-cpython-122380`** — *"Can we keep the old arity and feature-detect the extra parameter instead?"*
3. **`gh-python-cpython-142655`** — *"Do you mind creating a errors.py file with custom exceptions for the different case, raise them and properly handle the messages in `__main__`?"*
4. **`gh-python-peps-2022`** — *"We should clarify what is an implementation detail and what is a public API clearly to avoid confusion."*

## 9. Guardrails
No library bikeshedding; no *"better error message"* without the sentence; no *"more validation"* without the breaking input; no guards for states excluded by `assert`s, the data model or visible callers; no silent fallback values; counter-example when rejecting a rule; breaking caller when rejecting an API change; doc-vs-code mismatches asked, not asserted; no process facts from memory; no NEWS/README rewrites that add private names or move user-facing limitations; no comments on untouched code without framing; no signature cleanups in backports; `WDYT?` on shared calls; no comment budget — every proven finding, every repeated-pattern anchor and the central design objection are always emitted; one-line fixes ship a `suggestion` fence. Voice: [voice-and-examples.md](voice-and-examples.md).
