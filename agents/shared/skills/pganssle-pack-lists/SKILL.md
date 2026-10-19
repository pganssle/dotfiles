---
name: pganssle-pack-lists
description: Build a packing list for an upcoming trip for Paul Ganssle (pganssle) from his archive of past org-mode packing lists. Use this whenever he asks for a packing list, pack list, "what should I bring", or help preparing for a trip — even if he only gives a destination and dates. Covers finding and weighing past trips (recent ones for current gear, older similar ones for trip-specific items), adjusting for length, laundry, weather, companions, and domestic vs. international travel, and writing the new list in his existing org format.
---

# Packing Lists

Paul keeps one org-mode packing list per trip, and a new list should be derived
from those rather than invented. The point of the exercise is to produce
a list that reflects **what he owns and carries now** while picking up the
**trip-specific items** that only show up on similar past trips.

## Step 1: Locate the archive and pin down the trip

The lists live in `~/Documents/Notes/org/personal/packing/`, one file per trip,
named `YYYY[-MM]-<place-or-event>.org` (e.g. `2025-10-sfo.org`,
`2026-08-spain.org`). Use the filename and the first-line header to date and
identify each trip; file mtimes and git history are a fallback only.

From the request, extract (and ask only about what's missing *and* would change
the list):

- **Destination(s)** and whether it's **international** (passports,
  international adapter, EU adapter in carry-on) or domestic.
- **Dates and length**, including how he's getting home (a red-eye means a neck
  pillow, sleep mask, earbuds within reach).
- **Who is going.** Solo/work trips and family trips have very different lists.
- **Purpose**: conference/sprint (laptop stand, business cards, maybe second
  monitor), office visit (badge, work laptop, work security key), road trip
  (cold bag, more liberal packing), sport/ski, special events (e.g. an eclipse
  kit).
- **Laundry access** and from when.
- **Activities he's ruled in or out** (e.g. "no swimming" → no bathing suit).

He's often packing the same day, so prefer producing a complete draft and
flagging open questions at the end over blocking on questions up front. Ask up
front only if the answer restructures the whole list (e.g. whether the kids are
coming).

## Step 2: Read the right past lists

Read two groups, and treat them differently:

1. **The 3–5 most recent trips, regardless of destination.** These are the
   source of truth for his *current* gear: electronics, cables, chargers,
   wearables, medications, wallet contents, toiletries. Gear changes over time
   (devices get retired, cables get consolidated, cards change), so an item that
   has disappeared from several recent lists should be presumed gone even if the
   matching older trip had it. Diff recent lists against each other to see the
   trend, rather than trusting any single one.
2. **The most similar past trips**, even if old: same destination, same kind of
   event, similar length, same companions. These supply trip-specific items and
   clothing mix (e.g. what he wore last time in the same city/season).

Older lists (roughly pre-2022) use a different layout (`* Clothing` /
`* Electronics` / `* Toiletries` with `Person`/`Backpack`/`Check luggage`
subsections) and dress clothes; use them for ideas, not structure.

Reading tips:

- `[X]` = packed, `[ ]` = not packed/forgotten, `[-]` = deliberately skipped
  (partial checkbox). An item that is `[-]` or unchecked on recent trips is
  a weaker signal than one that's `[X]`; mark doubtful carry-overs with a
  trailing ` ?` the way he does.
- Weekend trips and road trips often have half-filled sections (e.g. the
  electronics organizer left unchecked); don't read omissions there as gear
  having been retired. Base gear decisions on full-length flying trips.
- First-line headers are frequently copy-pasted with stale dates. Trust the
  filename for when a trip happened.
- If the user tells you something has changed (e.g. "I no longer have
  a Garmin"), remove *everything* tied to it — the device, its charger in both
  the organizer and the personal electronics bag, and any related wearable on
  the "Person" list.

## Step 3: Decide quantities and the clothing mix

- **Socks/underwear**: count of days until laundry (or end of trip), written as
  `(N + 1)` where `+ 1` is a spare. His de facto cap is about `7 + 1` even on
  two-week trips; past that he does laundry. Short trips scale down (weekend ≈
  `3 + 1`, 4 days ≈ `4 + 1`/`5 + 1`).
- **Gym shorts/shirts**: about one per planned workout, typically 3–4, capped
  near 4–5 with laundry. Keep the gym bag section unless the trip clearly has
  no gym.
- **T-shirts and button-ups**: name specific shirts, using the names from the
  most recent lists (they change as shirts are retired). `(N + 1)` for
  T-shirts is common.
- **Pants**: pick by weather — jeans for cool, linen pants and shorts for warm,
  a mix for places with big day/night swings. `(0 + 1)` means "wearing them, not
  packing them."
- **Outerwear**: a sweatshirt by default; a jacket for real cold.
- Check the weather for the destination and dates (historical averages if the
  forecast doesn't reach that far) and mention what you found.

## Step 4: Write the list in his format

Create a new file in the same directory, named like the others. Match the
structure of the most recent comparable list:

```org
N-day trip to <Place> (<purpose>) (YYYY-MM-DD → YYYY-MM-DD[, notes])

* Duffel Bag
** Clothing
** Electronics          (power strip, chargers, Electronics organizer subtree)
** Gym bag
** General              (powder bag, quest bag, laundry/ziploc/shopping bags, tupperware, tools)
** Toiletries
**** Toiletry Bag [ ]
* Backpack
** Electronics          (laptops, tablet, e-reader, Personal electronics bag subtree)
** General              (water bottle, pills, badge, notebook, pens, keys, ...)
* Person
** Electronics
** Pockets              (wallet subtree)
```

Add trip-specific top-level sections when needed, following past examples:
`** Kids' stuff` (with per-kid clothes, electronics, fun, toiletries), `* Day
bag`, `* Cold bag` for road trips, `** Ski stuff`, an event kit, etc.

Formatting conventions:

- Two-space indented `- [ ]` items, nested subtrees for bags and organizers,
  quantities in parentheses: `(4)`, `(7 + 1)`.
- All boxes start unchecked (`[ ]`); he checks them off as he packs.
- Keep his spelling and item names verbatim (e.g. "Emory board", "Ondesatran",
  "Gummie Guppies") so the lists stay diffable across trips — don't correct
  them.
- Put the trip's key facts in the header line (destination, purpose, dates,
  laundry, red-eye), since that line is how he identifies trips later.

## Step 5: Report back

Keep the summary short:

- Which past lists you based it on.
- Notable **removals** (retired gear, things not needed this trip) and
  **additions** (trip-specific items) relative to the closest past trip, with
  the reason for each.
- The clothing count reasoning and weather summary (with sources).
- A short list of **items to double-check**: things that vanished from recent
  lists but seem important for this trip, and anything you guessed about.

Don't commit the file unless asked.
