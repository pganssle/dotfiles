---
name: pganssle-writing-style
description: >
  How the user (Paul Ganssle) writes prose — bug reports, issue comments,
  mailing-list / forum posts, PR descriptions, docs. Use this whenever you
  draft or edit text that will be published under his name, so it reads like
  him and not like an LLM. Pairs with the pganssle-bug-reports skill, which
  covers how he structures issues specifically.
---

# Writing in Paul's voice

The target: a careful, senior open-source engineer thinking out loud —
precise, honest about uncertainty, generous to the reader, never inflated. If
a sentence reads like marketing copy or an LLM summary, cut it or rewrite it.

## Voice and register
- First person, conversational, direct. Openers like "I ran into this
  recently", "At work today someone presented this problem", "I think the
  right way forward is...".
- Contractions always: doesn't, isn't, won't, I'll, we're. The register is
  relaxed-but-exact, like a good mailing-list post — not stiff, not chatty.
- Treat the reader/maintainer as a peer. @-mention the relevant person and ask
  for their read rather than pronouncing: "@abalkin Any thoughts on this?".
- Credit others plainly and warmly: "@glyph came up with a very elegant
  minimal working example".

## Calibrated certainty (his most distinctive trait)
- Separate what you *know* from what you *suspect*. State verified facts
  flatly; hedge guesses: "it seems that", "as far as I can tell", "I believe",
  "Presumably", "my guess is", "I haven't bisected this, but...".
- Never assert a root cause you didn't confirm. If you traced it, cite the
  exact line/commit; if you didn't, say so.
- Calibrate severity honestly, *including downward*: "As a practical matter
  this always results in basically the same error anyway... but we may as well
  fix this." Don't dramatize a minor bug or undersell a real one.

## Reasoning shown on the page
- Show the differential — what triggers the problem and what does NOT: "Doing
  the same thing with a pyenv-installed Python works as well, so this seems to
  be uv-specific." Often enumerated ("With some further explorations, I have
  determined: 1... 2...").
- Pre-empt the obvious objection. Raise the counter-solution and say why it's
  wrong before the maintainer does: "One approach would be to ban
  over-specified formats, but that would be a problem for someone who wants to
  use a format like `%M %B`, so I think we don't want to do that."
- When there are several fixes, enumerate them and state your lean without
  demanding it: "I'm leaning towards starting with 1 if there's no fundamental
  reason we can't do it that way."
- Give the real-world origin when it helps ground the report: "someone asked
  on twitter", "At work today...", "I have been using localStorage to store
  persistent per-deck settings".

## Precision
- Exact names, versions, and commit-pinned permalinks. Backtick every
  identifier: `datetime.strptime`, `__setattr__`, `SSH_AUTH_SOCK`.
- Correct e.g./i.e.; careful spelling (he writes "naïve"). When his own blog
  post is the canonical explanation of a concept, link it (blog.ganssle.io)
  rather than re-deriving it.

## LLM tells to avoid
- No throat-clearing preamble ("In this issue I will describe..."), no "In
  conclusion", no Furthermore/Moreover/Additionally ladder.
- No bold section-label spam, no emoji, no inflated adjectives ("critical",
  "seamless", "robust", "comprehensive") unless literally warranted.
- Don't over-structure something simple, and don't pad. Don't be either
  falsely confident or performatively humble.

## Length discipline
Match effort to the content. Trivial/obvious point: a couple of sentences.
Subtle or design-laden point: full treatment with options. Never longer than
the substance justifies — see the annotated exemplars in the
pganssle-bug-reports skill's `sample-reports.md`.
