---
name: swarm-cloner
description: >-
  Clones a software engineer's code review style, technical judgment, and
  engineering philosophy into a modular suite of domain-specific skills using a
  multi-agent swarm and a zero-leakage blind evaluation benchmark. Use when asked
  to clone an engineer's review persona, mine a code review and technical writing
  corpus, build a pre-review blind evaluation dataset, or iteratively train and
  benchmark a persona skill suite. Don't use for reviewing a single PR with
  an existing review skill, or for creating simple single-command CLI skills.
---

# Swarm Cloner: End-to-End Engineer Persona & Review Skill Distillation

Distill an engineer's code review history, technical writings, talks, issue tracker discussions, and architectural principles into a **modular suite of domain-specific agent skills**, backed by a strictly partitioned, zero-leakage blind evaluation corpus and calibrated to 95–100% recall with 0% noise.

---

## 1. Model-Agnostic Two-Tier Swarm Architecture

Do not hardcode ephemeral model identifiers as static requirements. At the start of a cloning run, the swarm coordinator MUST inspect available models (`swarm{action:"models"}`) and exercise judgment to map them into two capability tiers:

### Tier 1: Target / Fast Worker Tier
- **Profile**: High-throughput, low-latency reasoning model (analogous to Gemini 3.8 Flash today).
- **Responsibilities**:
  1. **Parallel Corpus Mining Shards**: Mining PRs, changelists, issue trackers, mailing lists, and blog posts in parallel across repositories and date ranges.
  2. **Pre-Review Diff Reconstruction & Hygiene**: Reconstructing pre-review snapshots and running deterministic validation scripts.
  3. **Primary Target Model for Blind Code Reviews**: Running blind evaluations (`dev_eval` and `blind_test_eval`) with *only* the drafted skill suite loaded.
- **Why the Fast Tier Is the Primary Blind Target**: The purpose of skill distillation is to make the engineering heuristics, checklists, and framing rules explicit and operational enough that a fast, inexpensive everyday model reliably catches the same architectural and line-level concerns as the human engineer — without relying on frontier-model intuition to compensate for vague instructions.

### Tier 2: Frontier Judge & Architect Tier
- **Profile**: Roughly the most capable frontier reasoning model available in the swarm pool (analogous to Gemini Pro Next / 4.0+ today).
- **Responsibilities**:
  1. **Corpus Spot-Checking & Provenance Audit**: Auditing mined shards for diff contamination, post-review fixup leaks, and identity disambiguation.
  2. **Taxonomy Synthesis & Modular Skill Authoring**: Synthesizing the engineer's technical taxonomy from the training split and authoring/upgrading the umbrella router skill and domain-specific sub-skills.
  3. **Blind Evaluation Judge**: Scoring blind review outputs against ground truth, grading voice alignment, and adjudicating **unmatched extra findings** (where frontier-level engineering judgment is critical to distinguish a valid bug the human didn't notice from pedantic noise).
  4. **Held-Out Ceiling Benchmark**: Running the held-out `blind_test_eval` benchmark alongside the Fast Tier to separate skill instruction gaps from model-capability ceilings when the Fast Tier plateaus below 100%.

---

## 2. Phase 0: Upfront Discovery, Provenance Disambiguation & Blocking Contract

Before spawning bulk mining workers, the coordinator MUST execute Phase 0 with the user:

### Step 0.1: Corpus Source Discovery
If the prompt does not already specify where the target engineer's high-signal output lives, ask targeted questions to identify:
1. **Code Review Platforms & Handles**: GitHub/GitLab usernames (including separate personal vs. corporate handles), code review tools (Gerrit, Phabricator, or internal review systems), and priority repositories or subdirectories.
2. **Long-Form Technical Writings**: Personal blogs, PEPs/RFCs, architectural design docs, mailing list archives (`python-dev`, Discourse forums), conference talks, and issue tracker reports.
3. **Target Scope (`public/` vs. `private/`)**: Whether the user wants an internal-only skill, a 100% public open-source skill, or a dual-edition repository maintaining strict physical separation between `private/` (full internal + public) and `public/` (100% OSS-safe, zero internal leaks).

### Step 0.2: Name Commonality & Provenance Verification
1. **Assess Name & Handle Uniqueness**: Evaluate how common the engineer's display name and username/handle are across public and internal platforms.
2. **Run a Quick Disambiguation Probe**: Before mining at scale, run a fast search across candidate sources to check for homonyms (other engineers with the same name), shared/bot accounts, or rebased/re-authored commits.
3. **Confirm Uncertain Provenance**: If multiple candidate accounts, ambiguous author strings, or noisy repositories appear, ask a concise follow-up question to confirm which handles and repositories belong to the subject.

### Step 0.3: Autonomy vs. Blocking Preference on Long Runs
Multi-stage corpus mining, blind evaluation, and iterative skill refinement (`v1 → v2 → v3`) perform substantial work before hitting edge-case review ambiguities (`ambiguous_for_user.md`). **Always ask the user upfront in Phase 0**:
- **Option A — Autonomous Best-Effort Continuation**: If the swarm encounters ambiguous unmatched findings (`AMBIGUOUS_QUEUE`) while the user is away, should the Frontier Judge log them to `ambiguous_for_user.md`, make a best-effort call grounded in the subject's corpus, and continue the refinement loop asynchronously?
- **Option B — Strict Blocking Wait**: Or should the swarm pause at the ambiguity checkpoint and wait for explicit user input before finalizing the rubric and skill?

---

## 3. Phase 1: Strict Public vs. Private Directory Separation

When cloning an engineer whose work spans both internal corporate systems and open-source repositories, enforce strict physical separation across both the corpus and the published skills:

```text
review_corpus/
├── schema.json                        # Canonical JSON schema for review records
├── scripts/                           # Reusable split, prompt, validation & leak-check scripts
├── public/                            # 100% OPEN SOURCE & PUBLIC ARTIFACTS (Zero Internal Leaks)
│   ├── raw/                           # Public GitHub PRs, public blogs, PEPs, talks, forums
│   ├── curated/                       # Normalized public records
│   ├── splits/                        # Locked 50/25/25 public splits + blind_prompts/
│   ├── eval_runs/                     # Public blind evaluation shards and scorecards
│   ├── taxonomy/                      # Public taxonomy, rubric, and adjudications
│   └── skill/                         # Public OSS skill suite (umbrella + domain sub-skills)
└── private/                           # INTERNAL + COMBINED ARTIFACTS
    ├── raw/                           # Internal changelists, internal docs/issues
    ├── curated/
    ├── splits/
    ├── eval_runs/
    ├── taxonomy/
    └── skill/                         # Full internal+public skill suite
```

- **Automated Leak Verification Gate**: Run [scripts/verify_public_leak_free.py](scripts/verify_public_leak_free.py) against `public/` in both the corpus and skill repositories after every update. `public/` must have **zero** internal changelist IDs, internal issue tracker URLs, internal monorepo paths, or proprietary project names.

---

## 4. Phase 2: Parallel Corpus Mining & Pre-Review Diff Reconstruction

Spawn parallel **Fast-Tier** mining workers sharded by source/repository/era, with a **Frontier-Tier** verifier spot-checking outputs. Follow the full schema and hygiene rules in [references/corpus-schema-and-hygiene.md](references/corpus-schema-and-hygiene.md):

1. **The Golden Rule of Diff Mining — Reconstruct the Pre-Review Snapshot**:
   - **Never fetch the final merged PR diff!** A merged diff contains the author's post-review fixes responding to the reviewer's comments, which erases the original bug/antipattern from the diff (making blind recall impossible) or leaks the reviewer's requested design.
   - Always fetch the diff at the **exact pre-review commit or snapshot** where the reviewer anchored their initial review comments:
     - **GitHub PRs**: Inspect the commit timeline (`gh api repos/{owner}/{repo}/pulls/{pr}/commits` and review `commit_id` timestamps). Reconstruct the diff up to the commit reviewed (`base.sha...review_commit_sha`), or invert post-review fixup commits (`git diff` before commits matching `"address review comments"`).
     - **Snapshot-Based Review Tools**: Diff the base snapshot against the specific patchset/snapshot index (`--snapshot=N`) on which the reviewer published their comments, not the final submitted revision.
2. **Strip Post-Review Fixup Commits & Author Resolution Replies**:
   - Filter out commit messages that leak review feedback (`"Address review comments"`, `"Fix per <reviewer>"`).
   - Filter out author-side resolution replies (`"Done."`, `"Fixed."`, `"Switched to..."`) and purely social/administrative remarks (`"LGTM"`, `"Replaced by #..."`).
3. **Attach Temporal & Ecosystem Context (`review_date` + `era_context`)**:
   - Every record MUST include `review_date` (`YYYY-MM-DD`) and `era_context` (supported language versions, e.g. Python 2.7/3.x dual compatibility in 2018 vs. Python 3.12+ in 2025, framework constraints, and repo conventions). Blind reviewers rely on this header to avoid anachronistic suggestions.

---

## 5. Phase 3: Locked Stratified 50 / 25 / 25 Splits & Blind Prompts

Use the bundled deterministic scripts ([scripts/build_splits.py](scripts/build_splits.py), [scripts/prepare_blind_prompts.py](scripts/prepare_blind_prompts.py), and [scripts/validate_corpus.py](scripts/validate_corpus.py)):

1. **Stratify & Lock Splits (`50% Train / 25% Dev / 25% Blind Test`)**:
   ```bash
   python3 scripts/build_splits.py \
     --github raw/github_reviews.jsonl \
     --extra-raw raw/additional_reviews.jsonl \
     --output-dir splits \
     --curated-output curated/all_reviews_curated.jsonl \
     --lock-splits
   ```
   - `train_reference.jsonl` (~50%): Used for taxonomy synthesis and few-shot examples in the skill.
   - `dev_eval.jsonl` (~25%): Used for iterative blind evaluation (`v1 → v2 → v3`).
   - `blind_test_eval.jsonl` (~25%): Strictly held-out final test set; never inspect or tune on this split during skill iteration.
   - **Split ID Lock**: Once generated, `--lock-splits` preserves exact record partition assignments across any subsequent data hygiene rebuilds so zero `dev`/`test` records ever leak into `train`.
2. **Generate & Validate Zero-Leakage Blind Prompt Packets**:
   ```bash
   python3 scripts/prepare_blind_prompts.py \
     --dev-split splits/dev_eval.jsonl \
     --test-split splits/blind_test_eval.jsonl \
     --output-dir splits/blind_prompts \
     --reviewer-handle {subject_handle}

   python3 scripts/validate_corpus.py \
     splits/*.jsonl \
     --prompts-dir splits/blind_prompts \
     --reviewer-handle {subject_handle}
   ```
   - `validate_corpus.py` verifies that every ground-truth inline comment's target code line exists in `record["diff"]` (catching post-fix diff contamination) and that zero reviewer handles or post-review fixup commits appear in `splits/blind_prompts/*.md`.

---

## 6. Phase 4: Taxonomy Synthesis & Well-Factored Domain Sub-Skills

A **Frontier-Tier** agent reads *only* `train_reference.jsonl` and `writings_and_talks.jsonl` to synthesize `taxonomy.md` and author the skill suite. Follow [references/domain-subskill-factoring.md](references/domain-subskill-factoring.md):

1. **Mandatory Modular Factoring into Domain-Specific Sub-Skills**:
   - **Never ship a monolithic review skill!** Factor the cloned engineer's capabilities into:
     - **Umbrella / Router Skill (`{subject}-code-review`)**: Encodes the top-level review philosophy, Phase 1 era/ecosystem calibration, the anti-self-capping multi-pass execution rules, Phase 3 anti-bikeshedding filter, Phase 4 rhetorical voice, and a **Domain Sub-Skill Routing Table**.
     - **Individual Standalone Domain Sub-Skills** (`> 50` lines each, self-contained with their own `SKILL.md` and `references/`):
       1. `{subject}-python-typing` (or language typing, data modeling, protocols & signatures)
       2. `{subject}-api-design` (API surface minimalism, config-driven modularity, stdlib idioms & error semantics)
       3. `{subject}-testing-and-mocks` (test double hierarchy `Real > Fake > Stub > Mock`, property testing, parameterization & mutation/fallback coverage)
       4. `{subject}-cpp-and-ml` (systems/C/C++ safety, memory/bounds checks & ML compiler/runtime invariants)
       5. `{subject}-build-and-ci` (build hermeticity, CI/CD workflows, supply-chain pinning, VCS hygiene & docs/accessibility)
2. **Enforce Anti-Self-Capping & Exact Line-Anchoring in the Skill**:
   - Fast-Tier models default to stopping after finding 2–4 major issues on a multi-file diff, or bundling multiple functions/constants into one summary comment.
   - Explicitly instruct the reviewer in `SKILL.md`:
     1. **Never self-cap comments**: Audit every modified file (`*.py`, `ci/**`, `.bzl`/`BUILD`, tests) through all domain passes even after finding a blocking bug in that file.
     2. **Anchor separately at each offending declaration**: Emit a separate, concise inline comment at each function signature, `@property`, constant, or branch that violates a rule rather than summarizing at the bottom of the file.

---

## 7. Phase 5: Blind Evaluation, Three-Bucket Rubric & Iteration (`v1 → v3`)

Follow the full rubric and scoring formulas in [references/evaluation-rubric-and-judge-protocol.md](references/evaluation-rubric-and-judge-protocol.md):

1. **Isolated Fast-Tier Blind Evaluation**:
   - Spawn parallel **Fast-Tier** blind reviewer agents on `dev_eval` (`splits/blind_prompts/<id>.md`).
   - **Strict Sandbox**: Blind reviewers may read *only* the skill suite and their assigned `splits/blind_prompts/<id>.md` file. They are forbidden from reading `raw/`, `curated/`, `splits/*.jsonl`, or querying live review tools.
2. **Frontier-Tier Judging with the Asymmetric Three-Bucket Protocol**:
   - Because historical reviews are **observational ground truth** (humans often stop early or miss secondary bugs, whereas LLMs often emit pedantic noise), the Frontier Judge grades asymmetrically:
     - **Primary Metric — Substantive Recall**: Each substantive ground-truth concern is scored `1.0` (Full Hit), `0.5` (Partial Hit), or `0.0` (Miss). Purely social remarks or multi-turn replies to post-diff author proposals are excluded from the denominator.
     - **Secondary Metric — Voice & Framing (`1–5`)**: Graded across Socratic pragmatism, causal rationale (*"explain the why"*), concrete code alternatives, and temporal/ecosystem calibration.
     - **Unmatched Extra Findings — The Three-Bucket Protocol**:
       - **Bucket A (`VALID_BONUS`, `0.0` penalty)**: Genuine bug, subtle edge case, or design flaw aligned with the subject's philosophy that the human didn't mention in their historical pass.
       - **Bucket B (`NOISE_PENALTY`, `-0.25` penalty per item)**: Pedantic, factually wrong, anachronistic, cross-ecosystem rule leakage, or bikeshedding that violates the subject's guardrails.
       - **Bucket C (`AMBIGUOUS_QUEUE`, `0.0` pending)**: Plausible finding where the Judge is uncertain if the subject would endorse it. Logged to `ambiguous_for_user.md` and handled per the Phase 0 blocking/autonomy contract.
3. **Iterative Refinement Loop (`dev_eval`: `v1 → v2 → v3`)**:
   - Diagnose every `0.0` Miss and `0.5` Partial Hit on `dev_eval`, abstract the underlying principle (never hardcode `dev_eval` file names or PR IDs into the skill), tighten anti-bikeshedding guardrails for any `NOISE_PENALTY`, and re-run blind evaluation on `dev_eval` until Any-Hit Recall reaches `>= 90–95%` with `0.0%` noise.
4. **Final Held-Out Benchmark (`blind_test_eval`: Fast Tier + Frontier Tier)**:
   - Once the skill freezes on `dev_eval`, run the untouched `blind_test_eval` split once with **Tier 1 (Fast Worker Tier)** and once with **Tier 2 (Frontier Tier)** to report both fast-model production recall and frontier-model ceiling recall.

---

## 8. Phase 6: Live Field-Test Postmortem Calibration (`v3 → v4+`)

When the cloned skill is deployed on a live PR and the human engineer subsequently conducts their own review on that same change:

1. **Diff the Bot Review Against the Human Review**:
   - **Kept Bot Comments**: Validated hits (`1.0`).
   - **Deleted / Edited Bot Comments**: Analyze *why* the human deleted or softened them; encode new negative guardrails (`NOISE_PENALTY`) or voice calibrations.
   - **Manual Comments Added by the Human**: Root-cause why the skill missed each manual comment (e.g., missing domain pattern vs. model self-capping on a long file vs. bundling lines).
2. **Generalize & Blind-Verify**:
   - Upgrade the umbrella skill and domain sub-skills using generalizable architectural/typing/testing heuristics (zero identifiers from the live PR hardcoded in the skill).
   - Reconstruct the pre-review blind prompt packet for that live PR and run fresh blind evaluations on both the **Fast Tier** and **Frontier Tier** to confirm `>= 90–100%` recall on the human's manual comments and `100%` on kept bot comments with `0` false positives.

---

## References & Bundled Scripts

- **Corpus Schema, Pre-Review Diff Reconstruction & Hygiene**: [references/corpus-schema-and-hygiene.md](references/corpus-schema-and-hygiene.md)
- **Three-Bucket Evaluation Rubric, Judge Protocol & Live Postmortems**: [references/evaluation-rubric-and-judge-protocol.md](references/evaluation-rubric-and-judge-protocol.md)
- **Modular Domain Sub-Skill Factoring & Dual Public/Private Sync**: [references/domain-subskill-factoring.md](references/domain-subskill-factoring.md)
- **Deterministic Split & Hygiene Builder**: [scripts/build_splits.py](scripts/build_splits.py)
- **Zero-Leakage Blind Prompt Generator**: [scripts/prepare_blind_prompts.py](scripts/prepare_blind_prompts.py)
- **Pre-Review Diff Target & Prompt Leak Validator**: [scripts/validate_corpus.py](scripts/validate_corpus.py)
- **Automated Public Tree Leak Scanner**: [scripts/verify_public_leak_free.py](scripts/verify_public_leak_free.py)
