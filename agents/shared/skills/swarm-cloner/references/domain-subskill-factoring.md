# Factoring Cloned Personas into Domain-Specific Sub-Skills

A cloned engineering persona should **never** be shipped only as a single monolithic skill. While a full code review requires orchestrating multiple technical passes, engineers and agents frequently need targeted domain guidance (e.g., designing a Python data model, writing property-based tests, auditing C++ extension safety, or hardening CI/CD workflows) without loading unrelated domain rules into context.

---

## 1. The Umbrella Router + Standalone Domain Sub-Skills Pattern

Decompose the synthesized taxonomy into a **Top-Level Umbrella / Router Skill** plus **4–6 Standalone Domain-Specific Sub-Skills**:

```text
skills/
├── README.md
├── skills.json                        # Auto-discovers root skills and nested domain sub-skills
├── swarm-cloner/                      # Meta-skill for cloning & evaluating engineering personas
├── {subject}-code-review/             # Umbrella & Router Skill (full multi-pass review orchestrator)
│   ├── SKILL.md
│   ├── references/                    # Complete reference suite for single-skill fallback
│   ├── {subject}-python-typing/       # Domain Sub-Skill 1: Data Modeling, Typing, Protocols & Signatures
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── voice-and-examples.md
│   ├── {subject}-api-design/          # Domain Sub-Skill 2: API Surface, Modularity, Idioms & Error Semantics
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── voice-and-examples.md
│   ├── {subject}-testing-and-mocks/   # Domain Sub-Skill 3: Test Doubles, Hypothesis, SubTests & Mutation Rigor
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── voice-and-examples.md
│   ├── {subject}-cpp-and-ml/          # Domain Sub-Skill 4: C/C++ Safety & ML Compiler/Runtime Invariants
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── voice-and-examples.md
│   └── {subject}-build-and-ci/        # Domain Sub-Skill 5: Build Hermeticity, CI/CD, Supply Chain & VCS/Docs
│       ├── SKILL.md
│       └── references/
│           └── voice-and-examples.md
└── public/                            # 100% Public-Safe OSS Editions of All Skills Above (Zero Internal Leaks)
    ├── skills.json
    ├── swarm-cloner/
    └── {subject}-code-review/
        ├── SKILL.md
        ├── references/
        ├── {subject}-python-typing/
        ├── {subject}-api-design/
        ├── {subject}-testing-and-mocks/
        ├── {subject}-cpp-and-ml/
        └── {subject}-build-and-ci/
```

---

## 2. Design Requirements for Each Standalone Domain Sub-Skill

1. **Cardinality & Self-Containment (`> 50` Lines)**:
   - Every domain sub-skill must be a complete, standalone skill (`> 50` lines, typically `100–250` lines) with its own YAML frontmatter (`name` and `description < 1024` chars), domain philosophy, era/version calibration, actionable review/authoring checklist, anti-bikeshedding guardrails, and `references/voice-and-examples.md`.
2. **Mutually Clear Triggering Contracts (`Use when...` / `Don't use for...`)**:
   - **Umbrella Skill (`{subject}-code-review`)**: Triggers when asked to perform a comprehensive multi-pass code review of a PR, changelist, or multi-file diff as `{subject}`, and routes to (or loads) the domain sub-skills based on the files and languages in the diff.
   - **Domain Sub-Skills (`{subject}-<domain>`)**: Trigger both when routed from `{subject}-code-review` AND when a user asks to review, design, or refactor a specific domain (e.g., *"Review these Python type annotations and dataclasses in `{subject}`'s style"* → `{subject}-python-typing`; *"Audit these pytest fixtures and mocks as `{subject}`"* → `{subject}-testing-and-mocks`).
3. **Anti-Self-Capping & Exact Line-Anchoring Rules in Every Sub-Skill**:
   - Include the completeness contract in both the umbrella skill and each domain sub-skill:
     - **Never self-cap findings**: Report every instance of a domain violation across all modified files, even if the file also contains a blocking logic bug.
     - **Anchor at the exact offending declaration**: Never bundle distant lines from different parts of a file into a single comment. Emit a separate, crisp 1–3 sentence comment at each offending constant, alias, function signature, `@property`, or branch.

---

## 3. Dual Public (`public/`) vs. Private Maintenance Protocol

Whenever you create or upgrade the umbrella skill or any domain sub-skill:
1. Author the full internal+public edition at `skills/{subject}-code-review/{subject}-<domain>/` (and sync to `review_corpus/private/skill/{skill-name}/` and `~/.gemini/jetski/skills/`).
2. Generate the corresponding 100% public-safe OSS edition under `skills/public/{subject}-code-review/{subject}-<domain>/` (and `review_corpus/public/skill/{skill-name}/`) by stripping all internal changelist citations, internal bug links, internal monorepo depot paths, and proprietary project names.
3. Run `python3 swarm-cloner/scripts/verify_public_leak_free.py --public-dir {subject}-skills/public` and `--public-dir review_corpus/public` to guarantee **zero** internal leaks before committing.
