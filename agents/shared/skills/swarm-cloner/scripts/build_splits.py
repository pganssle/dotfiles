#!/usr/bin/env python3
"""Builds, normalizes, validates, and stratifies a code review corpus.

Reads raw reviews mined from code review platforms (GitHub, GitLab, Gerrit, or
internal review tools), normalizes their schemas, strips post-review fixup
commits and author resolution replies, enriches era context, deduplicates
records, and stratifies them into:
  - train_reference.jsonl (~50%)
  - dev_eval.jsonl (~25%)
  - blind_test_eval.jsonl (~25%)

Features Split ID Lock:
When rebuilding splits, preserves the exact ID partition assignments already
in train_reference.jsonl, dev_eval.jsonl, and blind_test_eval.jsonl so downstream
taxonomy and skill work remains 100% leak-free and stable.
"""

from __future__ import annotations

import argparse
import collections
import json
import logging
from pathlib import Path
import random
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("build_splits")

AUTHOR_REPLY_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"^(?:Done|Fixed|Moved to|Switched to|Updated|Changed to|Resolved|Removed|Added|Addressing|Rebased)\b", re.I),
    re.compile(r"^(?:The .* has been (?:exempted|updated|fixed|removed|changed))\b", re.I),
)

ADMIN_COMMENT_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"^(?:Replaced by #|I believe this is a duplicate of #|duplicate of #|I think we already did that|Closing in favor of|Superceded by|This is not going to be relevant after)", re.I),
    re.compile(r"^(?:Thanks for this .* looks great to me)", re.I),
    re.compile(r"^(?:Closing this|LGTM\b|Looks good to me\b)", re.I),
)


def build_post_review_commit_patterns(reviewer_handle: str) -> List[re.Pattern[str]]:
    """Builds regex patterns matching post-review fixup commits that leak feedback."""
    escaped = re.escape(reviewer_handle)
    return [
        re.compile(r"\b(?:address|addressing|fix|fixes|fixed|incorporat\w*|apply|applied)\s+(?:(?:pr|all|the|some|further|code)\s+)*(?:review|comments?|feedback)\b", re.I),
        re.compile(rf"\b(?:fix|fixed|fixes|per|addressed)\s+per\s+(?:{escaped}|reviewer)\b", re.I),
        re.compile(r"\b(?:per|after)\s+(?:review|feedback|comments?)\b", re.I),
        re.compile(rf"\b{escaped}\b", re.I),
        re.compile(r"\b(?:review\s+feedback|review\s+comments?)\b", re.I),
        re.compile(r"\baddressed\s+comments\b", re.I),
        re.compile(r"\bchanges\s+from\s+review\b", re.I),
        re.compile(r"\brespond(?:ed)?\s+to\s+review\b", re.I),
    ]


def is_post_review_commit(msg: str, patterns: Sequence[re.Pattern[str]]) -> bool:
    """Returns True if commit message appears to be a post-review fixup."""
    msg_str = str(msg).strip()
    return any(p.search(msg_str) for p in patterns)


def is_author_resolution_reply(comment_text: str) -> bool:
    """Returns True if comment is an author-side reply describing a fix rather than a reviewer comment."""
    cmt_str = str(comment_text).strip()
    return any(p.search(cmt_str) for p in AUTHOR_REPLY_PATTERNS)


def is_administrative_comment(comment_text: str) -> bool:
    """Returns True if comment is purely administrative/social with no substantive code review content."""
    cmt_str = str(comment_text).strip()
    return any(p.search(cmt_str) for p in ADMIN_COMMENT_PATTERNS)


def has_substantive_comments(record: Dict[str, Any]) -> bool:
    """Checks if record contains at least one substantive code/design review comment."""
    cmts = record.get("ground_truth_comments", [])
    if not cmts:
        return False
    return any(not is_administrative_comment(c.get("comment", "")) for c in cmts)


def infer_era_context(review_date: str, project: str) -> str:
    """Infers era and technical context if missing in raw data."""
    year = 2026
    m = re.match(r"^(\d{4})", review_date)
    if m:
        try:
            year = int(m.group(1))
        except ValueError:
            pass

    proj_lower = project.lower()
    if "dateutil" in proj_lower and year < 2020:
        return (
            f"{year} {project} codebase. "
            "Dual Python 2.7 and Python 3.x compatibility required. "
            "Strict backwards compatibility."
        )
    if any(p in proj_lower for p in ["zoneinfo", "cpython"]):
        return (
            f"{year} CPython standard library / PEP 615 zoneinfo. "
            "Python 3.9+ standard library and C-API conventions."
        )
    if any(p in proj_lower for p in ["setuptools", "build", "wheel", "packaging"]):
        return (
            f"{year} Python packaging ecosystem ({project}). "
            "Standards compliance (PEP 517/518/621), build backends, cross-platform support."
        )
    return f"{year} {project} development environment."


def normalize_comment(raw_cmt: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes an individual comment object."""
    comment_text = raw_cmt.get("comment", "") or raw_cmt.get("body", "") or raw_cmt.get("text", "")
    file_path = raw_cmt.get("file", "") or raw_cmt.get("path", "") or raw_cmt.get("filename", "")
    line_num = raw_cmt.get("line") or raw_cmt.get("original_line") or raw_cmt.get("line_number")

    if line_num is not None:
        try:
            line_num = int(line_num)
        except (ValueError, TypeError):
            line_num = None

    code_context = raw_cmt.get("code_context", "") or raw_cmt.get("diff_hunk", "") or raw_cmt.get("context", "")
    thread_context = raw_cmt.get("thread_context", "") or raw_cmt.get("replies", "")
    category = raw_cmt.get("category", "")
    severity = raw_cmt.get("severity", "")

    return {
        "file": str(file_path).strip() if file_path else "",
        "line": line_num,
        "code_context": str(code_context).strip() if code_context else "",
        "comment": str(comment_text).strip(),
        "thread_context": str(thread_context).strip() if thread_context else "",
        "category": str(category).strip() if category else None,
        "severity": str(severity).strip() if severity else None,
    }


def normalize_record(
    raw: Dict[str, Any],
    default_source: str,
    commit_patterns: Sequence[re.Pattern[str]],
) -> Optional[Dict[str, Any]]:
    """Normalizes and validates a single review record."""
    source = raw.get("source", default_source).lower()

    raw_id = raw.get("id") or raw.get("pr_number") or raw.get("number")
    if not raw_id:
        return None
    record_id = str(raw_id).strip()
    if source == "github" and not record_id.startswith("gh-"):
        record_id = f"gh-{record_id}"

    review_date = raw.get("review_date", "") or raw.get("date", "") or raw.get("created_at", "")
    if review_date:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", str(review_date))
        review_date = m.group(1) if m else "2025-01-01"
    else:
        review_date = "2025-01-01"

    project = raw.get("project", "") or raw.get("repo", "") or raw.get("repository", "") or "unknown/project"
    era_context = raw.get("era_context", "").strip() or infer_era_context(review_date, project)
    title = raw.get("title", "") or raw.get("subject", "") or "Untitled change"
    description = raw.get("description", "") or raw.get("body", "") or ""
    diff = raw.get("diff", "") or raw.get("patch", "") or ""
    if not diff.strip():
        return None

    raw_comments = raw.get("ground_truth_comments") or raw.get("comments") or []
    if not isinstance(raw_comments, list):
        raw_comments = []

    normalized_comments = []
    for cmt in raw_comments:
        if isinstance(cmt, dict):
            nc = normalize_comment(cmt)
            if nc["comment"] and not is_author_resolution_reply(nc["comment"]):
                normalized_comments.append(nc)
        elif isinstance(cmt, str) and cmt.strip():
            c_text = cmt.strip()
            if not is_author_resolution_reply(c_text):
                normalized_comments.append({
                    "file": "",
                    "line": None,
                    "code_context": "",
                    "comment": c_text,
                    "thread_context": "",
                    "category": None,
                    "severity": None,
                })

    if not normalized_comments:
        return None

    raw_commit_messages = raw.get("commit_messages")
    if isinstance(raw_commit_messages, str):
        raw_commit_messages = [raw_commit_messages]
    elif not isinstance(raw_commit_messages, list):
        raw_commit_messages = []

    cleaned_commit_messages = [
        str(cmsg).strip()
        for cmsg in raw_commit_messages
        if cmsg and not is_post_review_commit(str(cmsg), commit_patterns)
    ]

    linked_bug_id = raw.get("linked_bug_id") or raw.get("bug_id") or raw.get("issue_id") or ""
    linked_bug_context = raw.get("linked_bug_context") or raw.get("bug_context") or raw.get("issue_context") or ""
    url = raw.get("url") or raw.get("html_url") or ""
    pr_number = raw.get("pr_number") or raw.get("number")
    author = raw.get("author") or raw.get("owner") or ""

    return {
        "id": record_id,
        "source": source,
        "review_date": review_date,
        "era_context": era_context,
        "project": project,
        "url": str(url) if url else None,
        "pr_number": pr_number,
        "author": str(author) if author else None,
        "title": str(title).strip(),
        "description": str(description).strip(),
        "commit_messages": cleaned_commit_messages,
        "linked_bug_id": str(linked_bug_id).strip() if linked_bug_id else None,
        "linked_bug_context": str(linked_bug_context).strip() if linked_bug_context else "",
        "diff": str(diff),
        "ground_truth_comments": normalized_comments,
        "metadata": {
            "comment_count": len(normalized_comments),
            "diff_lines": len(diff.splitlines()),
        },
    }


def load_and_normalize_file(
    filepath: Path,
    default_source: str,
    commit_patterns: Sequence[re.Pattern[str]],
) -> List[Dict[str, Any]]:
    """Loads a JSONL file and normalizes all valid records."""
    if not filepath.exists():
        logger.warning("File does not exist: %s", filepath)
        return []

    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error("JSON decode error in %s:%d: %s", filepath, line_no, e)
                continue

            rec = normalize_record(data, default_source=default_source, commit_patterns=commit_patterns)
            if rec:
                records.append(rec)
    logger.info("Loaded %d valid records from %s", len(records), filepath)
    return records


def get_stratum_key(rec: Dict[str, Any]) -> Tuple[str, str]:
    """Computes stratification key (source, recency_era)."""
    source = rec["source"]
    year = 2026
    m = re.match(r"^(\d{4})", rec["review_date"])
    if m:
        try:
            year = int(m.group(1))
        except ValueError:
            pass

    if year >= 2024:
        recency = "recent (>=2024)"
    elif year >= 2020:
        recency = "mid (2020-2023)"
    else:
        recency = "historical (<2020)"
    return (source, recency)


def stratify_dataset(
    records: List[Dict[str, Any]],
    train_ratio: float = 0.50,
    dev_ratio: float = 0.25,
    test_ratio: float = 0.25,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Stratifies records across source and recency with deterministic RNG."""
    del test_ratio  # Derived as remainder (1 - train_ratio - dev_ratio)
    rng = random.Random(seed)
    strata: Dict[Tuple[str, str], List[Dict[str, Any]]] = collections.defaultdict(list)
    for r in records:
        strata[get_stratum_key(r)].append(r)

    train_split: List[Dict[str, Any]] = []
    dev_split: List[Dict[str, Any]] = []
    test_split: List[Dict[str, Any]] = []

    for key in sorted(strata.keys()):
        items = list(strata[key])
        rng.shuffle(items)
        n = len(items)
        if n == 1:
            train_split.append(items[0])
        elif n == 2:
            train_split.append(items[0])
            if len(dev_split) <= len(test_split):
                dev_split.append(items[1])
            else:
                test_split.append(items[1])
        elif n == 3:
            train_split.append(items[0])
            dev_split.append(items[1])
            test_split.append(items[2])
        else:
            n_train = max(1, round(n * train_ratio))
            n_dev = max(1, round(n * dev_ratio))
            n_test = max(1, n - n_train - n_dev)
            while n_train + n_dev + n_test > n:
                if n_train > 1 and n_train >= n_dev and n_train >= n_test:
                    n_train -= 1
                elif n_dev > 1 and n_dev >= n_test:
                    n_dev -= 1
                elif n_test > 1:
                    n_test -= 1
                else:
                    break
            train_split.extend(items[:n_train])
            dev_split.extend(items[n_train : n_train + n_dev])
            test_split.extend(items[n_train + n_dev :])

    rng.shuffle(train_split)
    rng.shuffle(dev_split)
    rng.shuffle(test_split)
    return train_split, dev_split, test_split


def load_locked_splits(lock_dir: Path) -> Optional[Dict[str, List[str]]]:
    """Loads existing split ID assignments if present to lock partitions."""
    train_file = lock_dir / "train_reference.jsonl"
    dev_file = lock_dir / "dev_eval.jsonl"
    test_file = lock_dir / "blind_test_eval.jsonl"

    if not (train_file.exists() and dev_file.exists() and test_file.exists()):
        return None

    def read_ids(filepath: Path) -> List[str]:
        ids = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "id" in data:
                        ids.append(data["id"])
                except json.JSONDecodeError:
                    pass
        return ids

    return {
        "train": read_ids(train_file),
        "dev": read_ids(dev_file),
        "test": read_ids(test_file),
    }


def write_jsonl(records: Sequence[Dict[str, Any]], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    logger.info("Saved %d records to %s", len(records), filepath)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and stratify review corpus with split lock")
    parser.add_argument("--github", type=Path, default=Path("raw/github_reviews.jsonl"))
    parser.add_argument("--extra-raw", nargs="*", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, default=Path("splits"))
    parser.add_argument("--curated-output", type=Path, default=Path("curated/all_reviews_curated.jsonl"))
    parser.add_argument("--reviewer-handle", type=str, default="pganssle")
    parser.add_argument("--lock-splits", action="store_true", default=True)
    parser.add_argument("--no-lock-splits", action="store_false", dest="lock_splits")
    parser.add_argument("--lock-splits-dir", type=Path, default=None)
    parser.add_argument("--train-ratio", type=float, default=0.50)
    parser.add_argument("--dev-ratio", type=float, default=0.25)
    parser.add_argument("--test-ratio", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    commit_patterns = build_post_review_commit_patterns(args.reviewer_handle)
    all_raw_records: List[Dict[str, Any]] = []
    all_raw_records.extend(load_and_normalize_file(args.github, "github", commit_patterns))
    for extra_file in args.extra_raw:
        all_raw_records.extend(load_and_normalize_file(extra_file, "other", commit_patterns))

    if not all_raw_records:
        logger.warning("No records loaded from raw files. Exiting.")
        sys.exit(0)

    deduped: Dict[str, Dict[str, Any]] = {}
    for r in all_raw_records:
        rid = r["id"]
        if rid not in deduped or len(r["ground_truth_comments"]) > len(deduped[rid]["ground_truth_comments"]):
            deduped[rid] = r

    unique_records = list(deduped.values())
    write_jsonl(unique_records, args.curated_output)

    lock_dir = args.lock_splits_dir if args.lock_splits_dir else args.output_dir
    locked_splits = load_locked_splits(lock_dir) if args.lock_splits else None

    if locked_splits:
        record_map = {r["id"]: r for r in unique_records}
        train_split = [record_map[rid] for rid in locked_splits["train"] if rid in record_map]
        dev_split = [
            record_map[rid]
            for rid in locked_splits["dev"]
            if rid in record_map and has_substantive_comments(record_map[rid])
        ]
        test_split = [
            record_map[rid]
            for rid in locked_splits["test"]
            if rid in record_map and has_substantive_comments(record_map[rid])
        ]
        locked_all = set(locked_splits["train"]) | set(locked_splits["dev"]) | set(locked_splits["test"])
        unassigned = [r for r in unique_records if r["id"] not in locked_all]
        if unassigned:
            nt, nd, nte = stratify_dataset(unassigned, args.train_ratio, args.dev_ratio, args.test_ratio, args.seed)
            train_split.extend(nt)
            dev_split.extend([r for r in nd if has_substantive_comments(r)])
            test_split.extend([r for r in nte if has_substantive_comments(r)])
    else:
        train_split, dev_split, test_split = stratify_dataset(
            unique_records, args.train_ratio, args.dev_ratio, args.test_ratio, args.seed
        )
        dev_split = [r for r in dev_split if has_substantive_comments(r)]
        test_split = [r for r in test_split if has_substantive_comments(r)]

    write_jsonl(train_split, args.output_dir / "train_reference.jsonl")
    write_jsonl(dev_split, args.output_dir / "dev_eval.jsonl")
    write_jsonl(test_split, args.output_dir / "blind_test_eval.jsonl")


if __name__ == "__main__":
    main()
