# Python Semantics, Data Model, Readability & Typed Boundaries (`pablogsal`) — Pass 1 Reference (v5)

> **v5**: the clarity & micro-contract checklist runs on **every** modified hunk (not only silent ones; Python/Cython with the same weight as C/C++); layout/size hunks, the armed-feature counterfactual and `exec`-plus-value on compile-only tests are Tier 1 ledger items; fallible accessors get a direct `NULL`-check request (no macro alternative); eight more positive facts in [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md).

> **v4 rules**: three-way gate — proven in the diff → emit (fence for one-liners); author intent genuinely open → ask with the assumption stated; a general runtime/language/library/tooling contract or anything the diff contradicts → **do not post, not even as a question** (consult [runtime-and-tooling-facts.md](runtime-and-tooling-facts.md)); mandatory second-look pass over every hunk that produced no comment (name-vs-body, declaration locality, regex readability, point-of-reliance comments, unchecked accessors ticked without reachability reasoning, consumer-side accumulator overflow, tooling rationale); fences compiled against the whole scope; comments on unchanged or verbatim-moved lines dropped.

> **v3 rules**: no comment budget (every proven finding, every repeated-pattern anchor as its own one-line comment, and the central design objection are always emitted); proof by quotation before any bug/leak/crash/"cannot fail" claim, with `major`/`blocker` requiring a quoted diff line and assumption-dependent claims downgraded to `question`/`minor`; a stale-reference search after every deletion; every one-line change ships a ```` ```suggestion ```` fence; content nits (typos, stray `>>>` prompts, wrong example output) are posted, not deleted as formatting.

Condensed single-skill fallback for [`pablogsal-python-typing`](../pablogsal-python-typing/SKILL.md). All rules are grounded in `train_reference_public.jsonl` (record ids in parentheses).

---

## 0. Pass 0 on Python files (v2): deletions, dead code, clarity layer
- **Deletions are questions**: a removed helper, branch, check, warning, option or fallback gets *"Why do we need to drop this? … no?"* unless the description justifies it.
- **Dead code first on large ports/rewrites**: every added attribute, reactive/property, method, constant, parameter or helper needs a second use in the diff; none → *"Is this used anywhere? I cannot find another use in the diff"* / *"maybe we can drop it?"*; redundant assignments (*"Is the assignment necessary? …"*, `gh-bloomberg-memray-439`); loops that never loop.
- **Clarity layer, posted as `Nit:` with a fence**: verbs in the names of raising/acting helpers; a method named for one thing must not also populate other state; invert nested positive checks into one negative guard + early `raise`; `tuple(...)` for never-mutated sequences; declare locals/`cdef`s next to first use; test names state the scenario; constants duplicated from another language's limits carry a comment that references the constant it mirrors; prose that ships (NEWS, docstrings, error messages) is read as a user.
- **State across calls**: per-line/per-chunk functions carrying colour/escape/mode state — does the next call's first action undo the previous call's last action (a terminating reset/escape emitted only on the final chunk)? **Ambiguous tokens** in heuristics: enumerate unary/binary-ambiguous tokens, ask whether dropping them is enough.
- **User input & defaults**: enumerate plausible inputs (spaces, case, units) against the regex and check the error message states the accepted syntax; doc-vs-code default mismatch → **ask which is intended**, propose the doc fix. **Refactor-hidden behaviour change**: construct an input where old and new differ, ask for a test per affected surface. **Ask, don't narrate**: *"Can you comment a bit on why we need this line?"*

## 1. Semantics Must Match the Name and the Docs
- Use the operation the docs describe: `.lstrip(" \t")` for *leading* whitespace, never `.strip(" \t")`; fix code **and** every `.rst` sentence with `suggestion` fences (`gh-python-cpython-22469`).
- A name that under-describes behaviour is a finding: `_dedented_lines` that also strips (*"This also strips the line, not only dedents, no?"*), `original_line` that holds several lines (`gh-python-cpython-112097`).
- A property whose first statement primes another property (`self.line`) *"may be pointing out this should not be a property"*.
- Challenge comments that claim behaviour the code does not implement (*"How are errors account for here?"*).
- Check boundary positions: completion that assumes the stem is at the end of the buffer *"can suggest `and` for `a b`"* when the cursor is mid-line (`gh-python-cpython-122380`).

## 2. Readability Idioms (one-liners or `suggestion` fences)
| Diff pattern | Ask | Source |
| :--- | :--- | :--- |
| `try: … except Exception: pass` | `with suppress(Exception): …` | `gh-python-cpython-112097` |
| `s = ""; for …: s += part` | list + `"".join` — *"this can be cuadratic … This also helps with debugging."* | `gh-python-cpython-112097` |
| `None` checks scattered through a body | `if offset is None: offset = len(line)` once, rest unchanged | `gh-python-cpython-112097` |
| nested `if a: if b:` | *"Let's join these two conditions in the same conditional"* | `gh-python-cpython-112097` |
| block comments describing a function | *"All of these comments can be docstrings"* | `gh-python-cpython-112097` |
| `"(\n" + segment + "\n)"` | `f"(\n{segment}\n)"` and *"isn't this something we can solve with `mode= "eval"`?"* | `gh-python-cpython-112097` |
| `while True:` that returns on first iteration | drop the loop | `gh-python-cpython-122380` |
| generator join replacing a slice | *"`b[p+1:self.pos]` does the same thing and reads better. Is this needed for the fix?"* | `gh-python-cpython-122380` |
| six `if args.x: parser.error(...)` | `incompatible_flags` dict + one `parser.error` | `gh-bloomberg-memray-458` |
| `a if cond else 0` clamp | `max(a, 0)` (Cython caveat: *"not sure is a clear win"*) | `gh-bloomberg-memray-209` |
| opaque regex | `re.VERBOSE` with per-group comments and sample matches | `gh-bloomberg-pystack-206` |
| 60-line index-juggling function | *"extract some of these pieces into functions at the very least"* | `gh-bloomberg-memray-209` |

## 3. Robustness & Error Architecture
- Recursion over user-sized trees → `RecursionError`; iterate with an explicit stack or prove the bound, and *"add a test to see that we don't crash for a stack that's too deep"* (`gh-bloomberg-memray-439`).
- Redundant assignments (*"on the first call `node_index` is 0 so it should update frames[0] already, no?"*) and arrays mutated while indexed (*"isn't this invalidating the array … making the indexing incorrect?"*).
- Custom exceptions in `errors.py`, raised and rendered in `__main__`; never `raise sys.exit(...)`; factor bodies out of *"gigantic try/except blocks"* (`gh-python-cpython-142655`).
- Costs are questioned with a model, not asserted: *"compile the whole preceding buffer once per candidate … Maybe worth measuring the cost."* (`gh-python-cpython-122380`).

## 4. Typed Boundaries (Bloomberg Python) & Cython
- A signature change touches every call site: *"I think you missed some updates of calls to this function for example here: `tests/unit/test_templates.py`"* (`gh-bloomberg-memray-439`). Keyword-only option parameters are the house default.
- CPython `Lib/`, `Lib/test/`, `Tools/`: review behaviour, never demand annotations or docstrings. Mypy-checked projects: check consistency, not coverage.
- Cython: typed `cdef` locals, but weigh Python↔C conversion cost (*"may convert back and forth to Python stuff depending on what Cython decides to do"*); `except+` only where C++ can throw; unsupported modes raise `NotImplementedError` and get a test (`gh-bloomberg-memray-209`, `-277`).
- Dependency boundaries: a test dependency imported at runtime becomes a runtime dependency (`gh-y-crdt-pycrdt-356`); `importlib.util.find_spec` instead of importing optional modules during collection (`gh-bloomberg-memray-1033`); version gates exercised on every supported version.

## 5. Python↔Runtime Contracts
- Callback protocols are APIs: extend `(text, state)` by feature detection, never by arity (`gh-python-cpython-122380`).
- Public values vs storage: `None`/`-1` for missing positions regardless of `uint8_t` storage (`gh-python-peps-2022`).
- Traceback display must not hide the argument that caused the failure; wrong `end_lineno` is a compiler bug (`gh-python-cpython-112097`).
- Decoupling hooks (`format_frame`) are welcome when they avoid re-implementing recursion handling (`gh-python-cpython-27038`).

## 6. Era Calibration
| Era | Expect | Never demand |
| :--- | :--- | :--- |
| 2018–2021 CPython 3.7–3.10 | `unittest`, `.format`/`%`, `contextlib.suppress` | f-strings everywhere, `match`, `T \| None`, type hints |
| 2022–2023 CPython 3.11/3.12 · Memray/PyStack py3.7–3.12 | typed `src/`, keyword-only params, `argparse` subcommands | ungated `tomllib`/`ExceptionGroup`, `typing.Self` |
| 2024 CPython 3.13 | `_pyrepl`, `rlcompleter`, `sysconfig` flags | annotations in `Lib/` |
| 2025–2026 CPython 3.14/3.15 · Memray py3.9–3.14 | `profiling.sampling`, `sys.monitoring`, `support.subTests`, `find_spec` | `lazy import` before 3.15, bracketless `except` before 3.14 |

## 7. Annotated Mini-Examples
1. **`gh-python-cpython-22469`** — three `suggestion` fences: `lstrip` in `Lib/ast.py`, *"all leading whitespace characters will be omitted"* in `functions.rst`, *"For string inputs, all leading whitespace characters are now omitted."* in `ast.rst`.
2. **`gh-python-cpython-112097`** — on `self._line += …`: *"Nit: not that it matters, but this can be cuadratic. Better to place the lines in a list and join at the end."*; on `try/except: pass`: `with suppress(Exception):` fence; on the property: *"this may be pointing out this should not be a property. @… wdyt?"*
3. **`gh-python-cpython-122380`** — *"This assumes the stem is at the end of the buffer …"*; *"Nit: the `while True` here never loops …"*; *"Is this needed for the fix?"*
4. **`gh-bloomberg-memray-458`** — *"Maybe"* + the `incompatible_flags` dict block.

## 8. Guardrails
No formatter nits (punctuation, double spaces, quote style, import placement, `set([x])`/`type(x) !=` lints, typing-syntax modernisation); no *"add type hints/docstrings"* in CPython; no attrs/pydantic/click/rich; no anachronistic syntax for the project's Python floor ([era-api-timeline.md](era-api-timeline.md) §2); no speculative `None`/bounds guards without a named reachable input and no silent fallback values; no comments on untouched code without *"I know this pre-dates the PR, but …"*; no signature cleanups in backports; one-line `suggestion` over wholesale rewrites; `Nit:` / *"Not that it matters, but …"* for low severity; severity follows verification; no comment budget — every proven finding and every repeated-pattern anchor is emitted; one-line fixes ship a `suggestion` fence. Voice: [voice-and-examples.md](voice-and-examples.md).
