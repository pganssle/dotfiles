---
name: vocab-example-sentences
description: Generate example sentences for a vocabulary word list, tuned for a specific reader (usually a child at a given grade/reading level) and often destined for flashcards or an Anki deck. Use this whenever a user provides a list of words and wants example sentences, sample sentences, or usage sentences for study, quizzing, or memorization — even if they don't say "Anki." Also use for making vocab flashcards, spelling-list sentences, or "use it in a sentence" practice. Handles weaving the list together, keeping sentences illustration-friendly, making meaning clear from context, and flagging age-inappropriate words.
---

# Vocabulary Example Sentences

Generate short, engaging example sentences for a list of vocabulary words, tuned to a specific reader and often bound for flashcards (e.g., an Anki deck).

## Step 1: Establish the reader and the goal

Before writing, know these things. Pull them from the conversation if already stated; ask only for what's missing.

- **Who is the reader?** Age, grade, and reading level. These can differ — a 3rd grader reading at a 5th-grade level needs sentences pitched to the higher level. When in doubt, pitch to the reading level, not the grade.
- **Where will the sentences live?** Anki/flashcards, a worksheet, a spelling list, etc. This affects length (flashcards want short) and output format.
- **The word list itself.** Keep the words in the order given unless asked otherwise.

## Step 2: Write the sentences

Produce **one unique sentence per word**. Each sentence should be **relatively short but still somewhat challenging** for the target reader — stretch them a little, don't overwhelm them.

Apply these priorities. They aren't hard requirements; they're preferences that improve the deck when they can be satisfied naturally. Don't force any of them at the cost of a natural sentence.

1. **Weave the list together.** Wherever it reads naturally, use *other words from the list* inside a sentence — while still keeping that sentence uniquely "about" its own target word. This reinforces the whole list through repeated exposure. Look for natural clusters and build small recurring threads across several cards (e.g., a spy/adventure thread linking `infiltrating`, `traitor`, `sinister`, `canopy`, `bivouac`; or pairing mirror-words like `prologue`/`epilogue`). This is easy to forget — actively hunt for these links, because a list with no cross-links is a missed opportunity.

2. **Make it illustratable.** Favor sentences that suggest a clear, concrete image, since flashcards often pair well with a picture. Vivid, scene-like sentences beat abstract ones.

3. **Make meaning clear from context.** For rarer or harder words, the sentence should let the reader *infer* the meaning from surrounding context. For common words this is just a nice-to-have; for unusual words it matters a lot.

## Step 3: Handle sensitive words with care

Vocabulary lists — especially those pulled from novels — sometimes contain words that are dark, violent, or otherwise awkward for a young reader (e.g., `homicidal`, `sinister`, `traitor`, `infiltrating`).

- **Don't silently drop or swap them** — the reader needs a sentence for every word on their list.
- **Keep the sentence age-appropriate.** Lean on story/adventure/mystery framing (a novel's villain, a spy slipping past guards, a grumpy goose) rather than realistic violence.
- **Flag it to the user.** Briefly note which words gave you pause and, where helpful, offer a gentler alternate sentence or suggest a substitute word they could use instead — then let them decide.

## Step 4: Present the output

Default to a readable in-chat list: the **word in bold**, an em dash, then the sentence. When you've woven in other list words, **bold those cross-referenced words** too so the user can see the links at a glance.

**Example format:**

**infiltrating** — The **traitor** helped the spies by **infiltrating** the castle and unlocking the gate at midnight.

**prologue** — The book's **prologue** introduced a **traitor** whose secret wouldn't be revealed until the **epilogue**.

After the list, add a short note pointing out the threads you built (which words connect to which) and any sensitive-word flags.
