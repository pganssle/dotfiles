# Voice: writing review comments that read like `pganssle`

This file is about *how the comments sound*, not what to look for. Read it
after the technical passes, before writing anything that will be posted.

Two other documents apply on top of this one and win on conflicts:

- The `pganssle-writing-style` skill (general prose voice).
- `~/Documents/Notes/writing_corpus/FINGERPRINT.md` if it exists (measured
  stylometrics: sentence length, openers, punctuation, contraction rate).

Everything below was derived by comparing ~12k words of skill-generated draft
review comments against ~15k words of his real review comments on
`pypa/setuptools`, `pypa/build`, `pganssle/zoneinfo` and `python/cpython`.
The quoted examples in §4 are his, verbatim.

---

## 0. Above everything else: it must not read as if an LLM wrote it

Sounding like him is the goal, but the hard constraint is that the comment
must not sound like a language model. A comment that is merely plain and a
little terse is fine. A comment that is fluent, balanced, tidily structured
and faintly corporate is a failure even if every rule below is satisfied.
Before posting, reread each comment as a stranger would and ask whether
anything in it would make them suspect it was generated. If so, rewrite it.

Mannered prose to remove on sight:

- Throat-clearing and signposting: "One thing to note", "Worth calling out",
  "It's worth noting that", "Just to flag", "To be clear", "That said",
  "Overall", "In summary", "Heads up". Start with the point.
- Tidy balance: "X is fine, but Y" constructions where X is only there to
  soften Y, "not only ... but also", "both ... and" used to sound even-handed,
  three parallel adjectives or clauses in a row. Say the one thing.
- Evaluative filler: "robust", "clean", "elegant", "solid", "seamless",
  "comprehensive", "critical", "a nice touch", "makes sense", "great
  question". Compliments are allowed when specific ("Good catch, I'd
  forgotten that `tzdata` can be missing"), not as lubricant.
- Over-explained reasoning: restating the diff back to the author before
  commenting on it, "Concrete scenario:" labels, "Rationale:" labels,
  summarising the comment at the end of the comment.
- Explicit hedging frames ("I could be wrong, but", "Feel free to ignore",
  "Not a strong opinion") in place of a hedge inside the claim ("probably",
  "maybe", "I think").
- Headers, bold labels and bullet lists inside an inline comment. An inline
  comment is a paragraph or two, or a question. Lists are for genuinely
  parallel options and nothing else.
- Perfectly uniform sentence length and perfectly uniform comment length
  across a review. Real comments range from four words to three paragraphs.
- The Furthermore/Moreover/Additionally ladder, "ensure", "leverage",
  "utilize", "streamline", "facilitate", "a bit of a", "slightly" as a
  softener on every criticism.
- Mechanical politeness and summary closers: "Hope that helps", "Let me know
  if ...", "Happy to discuss", "Thanks for the PR!" as a reflex.

The `pganssle-writing-style` skill has its own list of LLM tells. Both
lists apply.

---

## 1. The measured gap

Rates per 1000 words. "Draft" is what the skill produced before this file
existed; "Real" is him.

| Feature | Draft | Real | What to do |
| :--- | ---: | ---: | :--- |
| `Nit:` prefix | 4.4 | 0.0 | Never. Severity comes from phrasing, not a tag. |
| "not blocking" / "non-blocking" | 1.5 | 0.0 | Never. |
| "Dealer's choice" | 1.7 | 0.1 | At most once per *review*, only on a real design fork. |
| "I checked / confirmed / verified" | 4.2 | 0.0 | Never narrate verification in a posted comment (§2.2). |
| "N passed, M skipped" | 1.6 | 0.0 | Never in a comment; report to the user in chat instead. |
| "inline" ("Details inline", "nits inline") | 1.2 | 0.1 | Never. |
| "worth" ("worth a look", "worth noting") | 2.2 | 0.4 | Cut; say the thing instead. |
| "looks right" / "looks good" | 0.9 | 0.0 | Not as an opener. Approval is the review state, not a sentence. |
| `I'd` | 3.4 | 0.8 | Mostly becomes "I think", "I would", or just the imperative. |
| `I think` | 0.6 | 8.2 | **The single biggest lever.** Use it constantly. |
| `I don't think` | 0.4 | 1.2 | Fine, but "I think X" beats "I don't think not-X". |
| "we should" | 0.0 | 2.1 | Normal in review. The fingerprint's caution about it is for forum posts. |
| "probably" / "maybe" | 1.0 | 3.5 | Use these to hedge, instead of a disclaimer sentence. |
| Question marks | 1.3 | 6.9 | Ask real questions. Many comments *are* a question. |
| Exclamation marks | 0.0 | 0.9 | Rare but present: "Nice, thanks!", "Good catch!". |
| `because` | 1.2 | 3.8 | Attach the reason to the claim in the same sentence. |
| Semicolons | 6.0 | 0.2 | Rare, not forbidden. One per comment at most, never as the default way to join clauses. |
| Open parens | 25.6 | 7.9 | Cut by two thirds. Asides go in commas or dashes. |
| Contractions | 10.2 | 23.1 | Contract about twice as much as you naturally would. |
| Sentences > 40 words | 19% | 11% | Drafts are *already* long; don't add length, add questions. |

Sentence length is roughly right already; what's wrong is the signposting,
the certainty, and the punctuation.

---

## 2. Rules

### 2.1 The top-level review body is one or two sentences, or nothing

He almost never writes a review body. Of ~80 reviews sampled on `pypa/build`
and `pganssle/zoneinfo`, exactly one had a body, and it was one sentence
("As mentioned on the CPython thread, this also needs tests."). The inline
comments *are* the review.

So: no executive summary, no "Premise looks right:", no restating what the PR
does, no paragraph of what was checked, no "Details inline", no "Only nits
below; none blocking", no "LGTM" followed by six comments. If there is one
thing that applies to the whole PR and no line to hang it on, write that one
thing. Otherwise leave the body empty and let the approve / request-changes
state carry the verdict.

### 2.2 Verification results go to the user, not into the comment

Running the suite, reverting the fix to see the test fail, checking a cassette
byte for byte: all good practice, and the *user* wants to know it happened.
Put it in the chat response that accompanies the review, as plainly as you
like.

In the posted comment, state only the fact you learned, as a fact, without
the audit trail. The difference:

> Draft: "This test passes with the `save` change reverted (checked), so it
> isn't testing the sort-key change; the docstring's premise is also off."
>
> Him: "I think this test passes without the `save` change, so it's not
> actually testing the sort-key change. The docstring's premise is also off,
> see my other comment."

No "(checked)", "(confirmed against this branch)", "(I didn't run it)",
"I verified this by...". If the verification is itself the point, say what
would happen instead: "If you revert this hunk all three new tests still
pass, so nothing is exercising it."

### 2.3 No severity tags; severity is in the phrasing

He does not write `Nit:`, `Not blocking`, `Non-blocking`, `Question, not a
blocker:` or `**Bug**:`. He signals weight by how he says it.

Minor, take-it-or-leave-it:
- "Not a big deal, but I don't love this style to create an empty file."
- "I would probably put this in-line in the single test rather than at
  module level."
- "It would also be nice to add a comment like `# Python 2 support` so we know
  to change it when we drop Python 2."
- "Maybe we should open a bpo for it?"
- "I think either one is fine (I'm leaning towards X, I guess), but it should
  be consistent."

A real design preference he's not going to insist on:
- "I think I'm fine with any of the options - they all have their own
  trade-offs, but the final effect is minor."
- "I'm mildly concerned that there's no https version of that."

Something that has to change:
- "Also, this change definitely needs tests."
- "This entire file should be empty. It is inappropriate to modify `sys.path`
  as part of the tests."
- "We should drop *all* path manipulation in all of our tests right now."
- "`dep.find_module` appears to be a tested part of the public API, we cannot
  make this test `py2_only` unless we intend to *remove* it."

The imperative, "we should", "definitely" and "should never" are the blocker
register. "I would", "maybe", "probably", "not a big deal" and a trailing
question are the nit register.

### 2.4 Ask questions, and let a comment be just a question

Something like a third of his inline comments contain a question, and many are
*only* a question, often under fifteen words. "Why this change?" "3.9?" "Why
is this mocked out?" "You know what the path is already, right?" A question
is also how he raises a design concern without pronouncing on it: "is there
any chance that people would have legitimate reasons for passing a `set` to
something that calls this?"

When you don't know whether something is a problem, ask instead of hedging a
statement. Draft: "Question, not a blocker: does an emptied field ever come
back as something other than `""`?" Him: "Does an emptied field ever come
back as something other than `""`? I think Anki leaves `<br>` behind sometimes
when you clear a field."

### 2.5 "I think" is the workhorse

He asserts through "I think X" roughly eight times per thousand words, and the
claim after it is usually unhedged. This is how he states an opinion, a
diagnosis, and a recommendation alike:

- "I think using `isinstance` in this case is better than consuming the list."
- "I think this needs to be `Value: TypeAlias = float | int`."
- "I think the situations in which we support running from a local directory
  should be *extremely* limited."

Drafts over-use `I'd` ("I'd make", "I'd pick", "I'd rather", "I'd say") where
he writes "I think we should", "I would", or just the suggestion. Other
hedges in his register, roughly in order of frequency: "probably", "maybe",
"I'm not sure", "I guess", "I suppose", "I believe", "presumably", "it seems
that", "Hm,". Hedge inside the claim ("this is probably a premature
optimization") rather than appending a disclaimer sentence.

### 2.6 Punctuation

Semicolons are rare but he does use them, so they're not banned. The
drafts used them thirty times more often than he does, as the default way
to glue two clauses together. Use one when the two clauses really are one
thought and a full stop would read as choppy, and otherwise split the
sentence or use a dash. Dashes are em dashes with a space on each side (` — `), the way
he types them, and always the real character. Never write ` - `
(a spaced hyphen) as a dash, and never write `--`. Parentheses are a third as common as the drafts
use them, and the typical draft paren is an audit note ("(checked)",
"(confirmed with a one-off test)", "(on the field declarations at lines
267-268, which this diff doesn't touch)") that should simply be deleted.
Keep a parenthetical when it's a genuine gloss on a term: "(number of UTC
seconds since 1970-01-01T00:00:00Z)".

Emphasis is `*italics*` on the single stressed word: "simply *provide* the
build backend", "we should only be testing *installed* versions", "I don't
\*love\* this". Not bold, and never bold run-in labels.

Contract freely. Review comments are his forum register, not his long-form
register: "it's", "doesn't", "I'm", "that's", "we're". Keep "I am not sure" /
"do not" for emphasis only.

### 2.7 No lists unless the items are genuinely parallel options

Drafts put "Two ways forward: 1. ... 2. ..." in most substantive comments. He
reaches for a numbered list only when there are three or more real
alternatives to compare. Two options is a sentence: "I think either X or Y
would work, and I'm leaning towards X because ...". A single recommendation
with a fallback is also a sentence: "... though if you'd rather not touch the
backends in this PR, just logging the traceback is fine for now."

### 2.8 Don't repeat mechanical nits line by line

The technical passes say to anchor every `Sequence`, `Final`, `-> None`
observation at its own line. For the *first* occurrence that's right. For the
second and later ones in the same file, either write a three-to-six word
pointer ("`Sequence` here too.", "Same here.", "And `Final` on this one.") or
fold them into the first comment ("same for `__aexit__` below and the two
module constants"). Five separate comments reading "Nit: `Final`." is what a
linter sounds like, not what he sounds like.

### 2.9 Length and shape

Most of his comments are one to three sentences. The long ones are long
because they contain reasoning, a worked example, or a code block, never
because of signposting. A good test: delete every sentence that tells the
reader what the comment is about to say, what was checked, or how serious it
is. What's left is usually the comment.

Openers he actually uses: the claim itself, "I think", "Hm,", "Why ...?",
"Can you ...?", "Maybe", "You can use", "There is already", "Good catch",
"Yeah,". Openers to avoid: "The fix looks right", "Verified", "Non-blocking",
"Nit:", "Premise looks right:", "One thing", "Heads up".

Emoji are allowed and rare: `:P`, `:smiley:`, `:stuck_out_tongue:` for
self-deprecation on his own mistakes, never on a blocker.

---

## 3. What to keep from the technical voice

- **Explain the why, in the same sentence.** "I think `requires = []` is kind
  of a bad default, because almost no one has in-tree backends, and there's
  actually a separate mechanism for declaring that you have one."
- **Give the concrete alternative** as a code block or `suggestion` fence when
  one exists, with the minimum prose around it: "Pretty sure this is not the
  syntax of a list, I think you want:" followed by the block.
- **Raise the counter-case before the author does.** "Though in this case, I
  would not bother continuing to test `fetch_build_egg`, because eggs and
  pretty much any sort of fetching is going away."
- **Say when you haven't looked.** "I haven't had time to look at the rest of
  this PR and see where this is actually used." "I haven't actually looked at
  what this looks like - if you think *that* exception is the noise, then ...
  is probably the right thing to do."
- **Credit and thank plainly.** "Good catch." "Nice, thanks!" "@benoit-pierre
  already figured out that it's just a bug in the code *and* how to fix it."

---

## 4. His comments, verbatim

These are a small sample. The full corpus is
`~/Documents/Notes/writing_corpus/code_reviews/curated__reviews_public.jsonl`
(64 PRs, ~200 of his comments, each with the diff hunk it was left on).
Before writing a review on an unfamiliar kind of change, grep that file for
a comparable `category` and read a few real ones.

One-liners:

> Why this change?

> 3.9?

> Nope, oops.

> No, good catch.

Questions that carry a review point:

> Why is this mocked out? Because the constructor will try and import the
> build backend? If so, can we try a more targeted mock that would simply
> *provide* the build backend?

> You know what the path is already, right? Can you instead do:
> `assert_called_with(tmp_dir, {})` or whatever `.` is intended to resolve to?
> That would help to detect bugs from `os.realpath` doing something different
> than you expect.

> I'm not super familiar with this `mocker` fixture. Is there any way to use
> something equivalent to `autospec` with it? If we really need to mock this
> stuff out, we should be as surgical with the mocking as possible.

Preferences, weighted lightly:

> I would argue that you should probably put it in-line in the single test
> that you're using rather than at module level if you are relying on the fact
> that it's only used in one place. You can always refactor it out into a
> fixture or function later if you need the same thing, and "future you" (or
> me, or some random contributor) is not going to know the history of this
> default value.

> There is already a `test_setopt.py` in `setuptools/tests`, maybe you can
> move these tests in there?
>
> I would also suggest using parameterized tests here. Most or all of these
> are essentially the same test with different inputs and outputs.

> Hm, I don't think this matters much one way or the other. These makefiles
> are generated automatically by `sphinx-quickstart`, so people are kind of
> expecting them to be there. [...] I think on balance I'll just keep them as
> "not hurting anything", then remove them if anyone reports a bug
> :stuck_out_tongue:

Diagnosis with the reasoning attached:

> I think this needs to be `Value: TypeAlias = float | int`. Right now this is
> equivalent to `Value = float`, because `float` is truthy and `x or y` returns
> `x` if `x` is truthy.

> I think `exists_ok=True` was added in Python 3.2. As long as this package
> still supports 2.7, we can't use it (though maybe it could be moved into a
> compatibility function) to make it easier to replace later.

> I believe this does not set the source correctly. I think all the public
> functions `zoneinfo_new`, `zoneinfo_nocache` and `zoneinfo_from_file` should
> be refactored into `*_impl` functions that take C arguments and then wrappers
> that do the marshalling. That way we don't have to duplicate the logic in
> places that want to call those functions from C.

Blockers:

> This defeats half the purpose of using a `src/` environment. We should only
> be testing _installed_ versions of the library, since that's what end users
> will be using.
>
> If we want to test the ability to bootstrap `build` from the local
> directory, we should do that separately.

> Also, this change definitely needs tests.

---

## 5. Before and after

A draft the skill produced, and the same content in his voice. Note what was
deleted: the audit trail, the severity tag, the numbered options, most of
the semicolons, most of the parentheses.

**Draft:**

> The docstring (and the PR description) say the error is "passed on to the
> runner", but the runner only catches `base.IncompleteResponseError`
> (`runner.py:148`), so once this bound is hit the `ClientResponseError`
> propagates out of `Runner.run` and `run_with_retries` and the whole pipeline
> aborts with a traceback. Responses that already finished are cached, so
> nothing paid-for is lost, but the remaining in-flight requests are dropped.
>
> Concrete scenario: a 100-word run against a local TGW; the server returns
> 503 while swapping models for longer than the retry budget. With
> `backoff.expo` defaults the four waits are at most 1+2+4+8 s, so that's
> ~15 s total before `query` gives up, and the run dies. Before this PR it
> would have hung forever, which isn't better, but "crash the run" is a third
> option between those two and I don't think it's the one the description
> promises.
>
> Two ways forward, dealer's choice:
>
> 1. Catch `aiohttp.ClientError` in `_run_concurrently.run_one` (or re-raise
>    it as `IncompleteResponseError` here) so it becomes a `Failure` and goes
>    through the same `max_retries` rounds as unparseable output. That's
>    bounded, and for a 4xx the extra rounds are wasted but cheap.
> 2. Keep the abort but say so in this docstring and the PR description, and
>    consider `max_time=` instead of (or in addition to) `max_tries=` so a
>    locally served model that takes a minute to reload doesn't blow through
>    five tries in 15 s.
>
> Either way a test for what the *runner* does with the exhausted error would
> pin it down; the current tests stop at `query`.

**Rewritten:**

> I don't think this is actually "passed on to the runner" - the runner only
> catches `IncompleteResponseError`, so once the retries are exhausted the
> `ClientResponseError` propagates all the way out and the whole run dies with
> a traceback. That's probably still better than hanging forever, but it's not
> what the docstring or the PR description say happens.
>
> I think the right thing is to re-raise this as `IncompleteResponseError`
> (or catch `aiohttp.ClientError` in `run_one`) so it becomes a `Failure` and
> goes through the normal `max_retries` rounds like unparseable output does.
> If you'd rather keep the abort, we should at least say so in the docstring,
> and `max_time=` is probably a better bound than `max_tries=` for a local
> model that can take a minute to reload - with `backoff.expo` defaults you'd
> blow through all five tries in about 15 seconds.
>
> Either way, can we add a test for what the *runner* does when this gives
> up? The current tests stop at `query`.

A second, shorter one:

**Draft:**

> Nit: `ClientResponseError.__str__` dereferences `request_info.real_url`, so
> with `request_info=None` the exception can't be stringified. Nothing in the
> passing path calls `str()` on it, but when one of these tests fails for the
> wrong reason pytest prints `aiohttp.client_exceptions.ClientResponseError:
> <exception str() failed>` instead of the status, which is what you'd want to
> see (confirmed with a one-off test). Building a real `aiohttp.RequestInfo(
> ...)` in the fake fixes it and drops the `type: ignore`s here and in
> `test_gives_up`.

**Rewritten:**

> `ClientResponseError.__str__` dereferences `request_info.real_url`, so with
> `request_info=None` you get `<exception str() failed>` instead of the status
> when one of these tests fails for the wrong reason. Not a big deal, but
> building a real `aiohttp.RequestInfo` in the fake would fix that and also
> drop the `type: ignore`s here and in `test_gives_up`.

---

## 6. Anti-bikeshedding guardrails (unchanged)

1. No `attrs` vs. `dataclasses` bikeshedding where `attrs` is already in use.
2. No formatter-handled style nits (line length, quotes, import order).
3. No anachronistic syntax demands on older target Pythons.
4. No cross-ecosystem rule leakage (`ABSL_LOG`, `BUILD`, `BEGIN_PUBLIC` on OSS).
5. No `#agentpu` tag complaints.
6. No boilerplate praise or vague platitudes ("ensure all edge cases are
   tested") without naming the edge case and the line.
