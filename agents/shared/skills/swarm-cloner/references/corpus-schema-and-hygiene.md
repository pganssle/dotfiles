# Corpus Schema, Pre-Review Diff Reconstruction & Data Hygiene

This reference specifies the data contracts, pre-review diff reconstruction algorithms, and automated hygiene checks required to build a zero-leakage code review corpus.

---

## 1. Canonical Review Record Schema (`schema.json`)

Every normalized code review record in `raw/*.jsonl`, `curated/*.jsonl`, and `splits/*.jsonl` MUST conform to this JSON schema:

```json
{
  "id": "gh-dateutil-dateutil-892",
  "source": "github",
  "review_date": "2019-05-14",
  "era_context": "2019 python-dateutil codebase. Dual Python 2.7 and Python 3.x compatibility required (six). Strict backwards compatibility.",
  "project": "dateutil/dateutil",
  "url": "https://github.com/dateutil/dateutil/pull/892",
  "pr_number": 892,
  "author": "contributor-handle",
  "title": "Add support for ISO 8601 week dates",
  "description": "Original PR description written by the author prior to review.",
  "commit_messages": [
    "Initial implementation of ISO week date parsing"
  ],
  "linked_bug_id": "#880",
  "linked_bug_context": "Issue description and pre-review design notes.",
  "diff": "--- a/dateutil/parser/isoparser.py\n+++ b/dateutil/parser/isoparser.py\n@@ ...",
  "ground_truth_comments": [
    {
      "file": "dateutil/parser/isoparser.py",
      "line": 142,
      "code_context": "+    if week > 52:",
      "comment": "ISO years can have 53 weeks (e.g., 2015 and 2020). What happens when week == 53 on a 52-week year vs a 53-week year?",
      "thread_context": "Author replied: Good catch, added _is_long_year check.",
      "category": "subtle-edge-case",
      "severity": "blocker"
    }
  ],
  "metadata": {
    "comment_count": 1,
    "diff_lines": 84
  }
}
```

---

## 2. Pre-Review Diff Reconstruction (Avoiding Post-Fix Contamination)

The #1 failure mode in code review dataset mining is fetching the **final merged diff** of a PR or changelist instead of the **pre-review diff** that the reviewer actually inspected.

### Why Merged Diffs Corrupt Blind Evaluations
1. **Erased Bugs**: After the reviewer leaves a comment (*"Line 42 has an off-by-one error"* or *"Should return `Sequence` instead of `list`"*), the author pushes a fixup commit before merging. In the final merged diff, the bug is gone and the fix is already present! A blind evaluator reviewing the merged diff cannot possibly "catch" a bug that has already been fixed.
2. **Direct Answer Leakage**: Sometimes the author's fixup commit adds a comment or helper named after the reviewer's suggestion, leaking the ground-truth answer directly into the diff.

### Reconstruction Algorithms by Platform

#### A. GitHub Pull Requests
1. Fetch the PR review list (`gh api repos/{owner}/{repo}/pulls/{pr}/reviews`) and inline review comments (`gh api repos/{owner}/{repo}/pulls/{pr}/comments`).
2. Extract the `commit_id` (or `original_commit_id`) on which the target reviewer's first substantive review was submitted, along with the PR's `base.sha`.
3. Fetch the commit list (`gh api repos/{owner}/{repo}/pulls/{pr}/commits`) and identify all commits authored *on or before* the timestamp of the reviewer's initial review pass (and exclude any commits whose message matches post-review fixup patterns).
4. Reconstruct the exact pre-review diff using the GitHub compare API:
   ```bash
   gh api repos/{owner}/{repo}/compare/{base_sha}...{pre_review_commit_sha} \
     -H "Accept: application/vnd.github.v3.diff"
   ```
5. **Fallback when `original_commit_id` was force-pushed/GC'd**:
   - Inspect each inline comment's `diff_hunk` stored permanently in the GitHub PR comments API.
   - Verify whether the target lines in `diff_hunk` exist in the current PR diff. If a post-review commit modified those lines, either diff the parent commit prior to the `"Address review comments"` commit or reconstruct the pre-review hunk directly from `diff_hunk`.

#### B. Snapshot-Based Code Review Systems (e.g., Gerrit Patchsets / Corporate Changelists)
1. Inspect the review comment metadata to identify the exact **patchset / snapshot number** (`snapshot_index`) on which the reviewer anchored their comments.
2. Fetch the unified diff at `--snapshot={snapshot_index}` (comparing base `0` against `snapshot_index`), never the final submitted snapshot.

---

## 3. Automated Hygiene Filters (`build_splits.py` & `validate_corpus.py`)

Every mined record must pass four automated hygiene filters before entering `splits/`:

1. **Target Line Existence Check (`verify_comment_in_diff`)**:
   - For every inline comment in `ground_truth_comments` that includes `code_context` / `diff_hunk`, `validate_corpus.py` extracts the target code line and verifies that it exists in `record["diff"]`. Any mismatch flags possible post-fix diff contamination.
2. **Post-Review Fixup Commit Stripping (`is_post_review_commit`)**:
   - Commit messages matching regexes such as `r"\b(?:address|fix|incorporat\w*|apply)\s+(?:.*\s+)?(?:review|comments?|feedback)\b"` or mentioning the reviewer's name/handle (`r"\bper\s+(?:<reviewer>|review)\b"`) are automatically stripped by `build_splits.py` and rejected by `validate_corpus.py`.
3. **Author Resolution Reply Stripping (`is_author_resolution_reply`)**:
   - When mining thread comments, ensure only comments authored by the target reviewer are extracted, and strip any accidentally captured resolution notes (`"Done."`, `"Fixed."`, `"Moved to..."`, `"Updated."`).
4. **Administrative / Social Comment Exclusion (`has_substantive_comments`)**:
   - PRs/changelists whose only comments from the reviewer are purely administrative (`"LGTM"`, `"Thanks for this, looks great to me"`, `"Replaced by #123"`, `"Duplicate of #456"`) contain zero substantive code review signal and are automatically excluded from `dev_eval` and `blind_test_eval`.

---

## 4. Temporal & Ecosystem Context (`era_context`)

Code review standards evolve over time (e.g., Python 2/3 `six` compatibility in 2017 vs. PEP 695 `type X = ...` in Python 3.12+; legacy `setup.py` vs. PEP 517/621 `pyproject.toml`).
- Every record MUST carry `review_date` (`YYYY-MM-DD`) and a descriptive `era_context` string.
- `prepare_blind_prompts.py` places `review_date` and `era_context` at the very top of every blind prompt packet so the blind reviewer calibrates its feedback to the exact historical era and repository ecosystem.
