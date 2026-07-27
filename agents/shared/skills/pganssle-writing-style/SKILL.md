---
name: pganssle-writing-style
description: >
  How the user (Paul Ganssle) writes prose — bug reports, issue comments,
  mailing-list / forum posts, PR descriptions, docs. Use this whenever you
  draft or edit text that will be published under his name, so it reads like
  him and not like an LLM. Pairs with other writing style skills tuned for
  specific contexts like bug reports and commit messages.
---

# Writing in Paul's voice

The target: a careful, senior professional thinking out loud — precise, honest
about uncertainty, generous to the reader, never inflated. If a sentence reads
like marketing copy or an LLM summary, cut it or rewrite it.

## Order of information

Most important thing first. The conclusion, the ask, or the headline finding
goes at the top; supporting detail, derivation, and caveats come later. Someone
who stops reading after the first paragraph should still walk away with the
thing they most needed to know, and someone who wants the reasoning can keep
going. This is about respecting other people's time and attention — most
readers are skimming, and the ones who aren't will read on regardless.

Under a heading that poses a question, answer it in the first sentence. From
the pytz migration guide, under "Which replacement to choose?":

> If you only need to support Python 3, you should use `zoneinfo`. If you
> need to support Python 2 and Python 3, you should either use
> `dateutil.tz` or a combination of `zoneinfo` and `dateutil`.

Rarely, for a long post, an explicit **TL;DR** paragraph at the top is fair game —
but only if the post can be fairly summarized in a short sentence or to convey
some useful context about the rest of the post.

## Context before detail

The same shape holds inside a paragraph and inside a sentence. Establish what a
thing *is* before piling on qualifiers, so the reader always has something to
attach each new piece of information to. From the pytz migration guide:

> Whenever a time zone's UTC offset changes (such as during a Daylight Saving
> Time / Summer Time transition), this creates either a gap ("imaginary" times)
> of times that have been skipped over in local time or a fold (ambiguous
> times), where there are two possible local times with the same "wall time".

The situation comes first, the two named outcomes hang off it, and the
parenthetical glosses arrive attached to the terms they gloss. Rewritten to lead
with the details instead, the same content forces the reader to hold two
elaborate noun phrases in suspense with nothing to pin them to:

> A gap ("imaginary" times) of times that have been skipped over in local time,
> or a fold (ambiguous times) where there are two possible local times with the
> same "wall time", is created whenever a time zone's UTC offset changes, such
> as during a Daylight Saving Time / Summer Time transition.

This is also the main legitimate use of the passive voice: when the active
version would lead with new, heavy information and bury the familiar
information at the end, flip it so the thing the reader already has in hand goes
first.

## Sentence shape

Readers parse a sentence into a tree as they go, and what costs them is holding
unresolved branches open in working memory. Long left-branching phrases and
center-embedded clauses are what make prose feel dense — not long words or long
sentences as such. The same content re-hung so it branches to the right reads
easily, because each piece resolves as it arrives.

This sentence from PEP 615 carries a claim, two reasons, a conditional and a
formal invariant, and still reads in one pass:

> It is important that a given `ZoneInfo` object's behavior not change during
> its lifetime, because a `datetime`'s `utcoffset()` method is used in both
> its equality and hash calculations, and if the result were to change during
> the `datetime`'s lifetime, it could break the invariant for all hashable
> objects that if `x == y`, it must also be true that `hash(x) == hash(y)`.

The claim lands in the first fourteen words and everything after it hangs off
something already established. Rewritten to front-load the same reasoning, it
becomes nearly unreadable without a second pass:

> That, because a `datetime`'s `utcoffset()` method is used in both its
> equality and hash calculations, a change in the result during the
> `datetime`'s lifetime could break the invariant for all hashable objects
> that if `x == y`, it must also be true that `hash(x) == hash(y)`, is why
> it is important that a given `ZoneInfo` object's behavior not change during
> its lifetime.

Nothing was cut; the subject is now a forty-six-word clause and the main verb
arrives last, so the reader has to hold all of it open. When a sentence feels
heavy, look for the deeply nested clause and either re-hang it to the right or
split the sentence in two.

This is not a technical-writing trick — the same shape carries a long joke. From
the gummy bear briefcase post:

> Eventually I'd leave it somewhere unattended for a while, hoping that someone
> would find my behavior so baffling that they'd feel *compelled* to open the
> briefcase and satisfy their curiosity about what was inside; of course,
> finding that the briefcase is full of gummy bears would simply raise
> *further* questions, and they would have no way to get answers about it
> without admitting to having snooped in the first place.

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

## Lists, with discretion

Paul reaches for bulleted and numbered lists more readily than he'd like, so
apply some friction here. A list earns its place when the items are genuinely
parallel — competing options, enumerated findings, steps to reproduce, a
differential of what does and doesn't trigger a bug — or genuinely ordered, for
a numbered list. It does not earn its place when it is three consecutive
sentences with the connective tissue stripped out, which is what most bulleted
lists actually are.

Prose is the default. If every bullet is a full sentence and each one follows
from the last, that is a paragraph, and writing it as a paragraph forces you to
make the relationships between the claims explicit instead of leaving the reader
to infer them. Avoiding lists altogether would be silly, but two well-placed
lists in a long post read as deliberate where six read as a tic.

## Length discipline
Match effort to the content. Trivial/obvious point: a couple of sentences.
Subtle or design-laden point: full treatment with options. Never longer than
the substance justifies.
