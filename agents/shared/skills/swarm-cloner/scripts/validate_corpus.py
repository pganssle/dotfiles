#!/usr/bin/env python3
"""Validates JSONL corpus files and blind evaluation prompts.

Checks:
1. Schema conformity: required fields, non-null, field types, date regex.
2. Pre-review diff & target line existence: verifies each ground-truth inline
   comment's code_context / diff_hunk target line actually exists in record['diff']
   (flagging post-fix merged diff contamination).
3. Pre-review commit message hygiene: ensures commit_messages in corpus records
   and generated blind prompt packets do not contain post-review fixup commits.
4. Zero-leakage verification on blind prompt packets.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Sequence, Tuple

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("validate_corpus")

REQUIRED_FIELDS: Sequence[str] = (
    "id",
    "source",
    "review_date",
    "era_context",
    "project",
    "title",
    "description",
    "diff",
    "ground_truth_comments",
)

DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUMBERED_DIFF_LINE_RE = re.compile(r"^\s*\d*\s*(?:\|\s*\d*\s*)?\|[ +-]?(.*)$")


def build_post_review_commit_patterns(reviewer_handle: str) -> List[re.Pattern[str]]:
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
    msg_str = str(msg).strip()
    return any(p.search(msg_str) for p in patterns)


def extract_target_lines(code_context: str) -> List[str]:
    """Extracts candidate target code lines from code_context or diff_hunk."""
    if not code_context:
        return []
    lines = [l.strip() for l in code_context.strip().splitlines() if l.strip()]
    if not lines:
        return []

    if any(l.startswith(("@@", "+++", "---")) for l in lines) or all(l[0] in "+- " for l in lines if l):
        candidates = []
        for l in reversed(lines):
            if l.startswith("@@"):
                continue
            clean = l[1:].strip() if l[0] in "+- " else l.strip()
            if len(clean) >= 4 and clean not in ("pass", "return", "{", "}", "None"):
                candidates.append(clean)
                break
        for l in lines:
            if l.startswith("+"):
                clean = l[1:].strip()
                if len(clean) >= 4 and clean not in candidates:
                    candidates.append(clean)
        return candidates

    return [l.strip() for l in lines if len(l.strip()) >= 4]


def normalize_diff_lines(diff_text: str) -> List[str]:
    """Normalizes lines in diff text by stripping diff prefixes and line numbers."""
    norm = []
    for l in diff_text.splitlines():
        m = NUMBERED_DIFF_LINE_RE.match(l)
        if m:
            c = m.group(1).strip()
            if c:
                norm.append(c)
        elif l.startswith(("+", "-", " ")):
            c = l[1:].strip()
            if c:
                norm.append(c)
        else:
            c = l.strip()
            if c:
                norm.append(c)
    return norm


def verify_comment_in_diff(cmt: Dict[str, Any], diff_text: str, norm_lines: Sequence[str]) -> Tuple[bool, str]:
    """Verifies that the target line of a ground-truth comment exists in record['diff']."""
    ctx = cmt.get("code_context")
    if not ctx:
        return True, ""

    targets = extract_target_lines(ctx)
    if not targets:
        return True, ""

    for target in targets:
        if target in diff_text:
            return True, ""
        for dl in norm_lines:
            if target in dl or (len(dl) >= 10 and dl in target):
                return True, ""

    return False, targets[0]


def validate_record(
    record: Any,
    line_num: int,
    filename: str,
    commit_patterns: Sequence[re.Pattern[str]],
    check_diff_targets: bool = True,
    check_commits: bool = True,
) -> List[str]:
    errors = []
    prefix = f"{filename}:{line_num}"

    if not isinstance(record, dict):
        return [f"{prefix}: line must be a JSON object"]

    for rf in REQUIRED_FIELDS:
        if rf not in record:
            errors.append(f"{prefix}: missing required field '{rf}'")
        elif record[rf] is None:
            errors.append(f"{prefix}: required field '{rf}' cannot be null")

    if "review_date" in record and isinstance(record["review_date"], str):
        if not DATE_REGEX.match(record["review_date"]):
            errors.append(f"{prefix}: 'review_date' must match YYYY-MM-DD: '{record['review_date']}'")

    diff_text = record.get("diff", "")
    if not isinstance(diff_text, str) or not diff_text.strip():
        errors.append(f"{prefix}: 'diff' must be a non-empty string")
    norm_diff_lines = normalize_diff_lines(diff_text) if isinstance(diff_text, str) else []

    if "ground_truth_comments" in record:
        cmts = record["ground_truth_comments"]
        if not isinstance(cmts, list) or not cmts:
            errors.append(f"{prefix}: 'ground_truth_comments' must be a non-empty list")
        else:
            for idx, cmt in enumerate(cmts):
                if not isinstance(cmt, dict) or not str(cmt.get("comment", "")).strip():
                    errors.append(f"{prefix}:comments[{idx}]: 'comment' must be a non-empty string")
                    continue
                if check_diff_targets and cmt.get("code_context"):
                    ok, target_line = verify_comment_in_diff(cmt, diff_text, norm_diff_lines)
                    if not ok:
                        errors.append(
                            f"{prefix}:comments[{idx}]: Target line '{target_line}' "
                            f"not found in record['diff'] (possible post-fix diff contamination)"
                        )

    if check_commits and "commit_messages" in record:
        c_msgs = record["commit_messages"]
        if isinstance(c_msgs, str):
            c_msgs = [c_msgs]
        elif not isinstance(c_msgs, list):
            c_msgs = []
        for cidx, cmsg in enumerate(c_msgs):
            if is_post_review_commit(str(cmsg), commit_patterns):
                errors.append(f"{prefix}:commit_messages[{cidx}]: Post-review fixup commit leakage: '{cmsg}'")

    return errors


def validate_blind_prompt(
    filepath: Path,
    reviewer_handle: str,
    commit_patterns: Sequence[re.Pattern[str]],
) -> List[str]:
    """Validates a markdown blind prompt packet for structural completeness and zero leakage."""
    if not filepath.exists():
        return [f"Prompt file not found: {filepath}"]

    content = filepath.read_text(encoding="utf-8")
    errors = []

    if not content.startswith("# Code Review Request:"):
        errors.append(f"{filepath.name}: Missing '# Code Review Request:' header")
    if "## Code Diff Under Review" not in content:
        errors.append(f"{filepath.name}: Missing '## Code Diff Under Review' section")

    diff_match = re.search(r"```diff\s*\n(.*?)\n```", content, re.DOTALL)
    if not diff_match or not diff_match.group(1).strip():
        errors.append(f"{filepath.name}: Missing or empty diff in ```diff code block")

    commit_match = re.search(r"## Commit Messages\s*\n(.*?)(?:\n##|\n---)", content, re.DOTALL)
    if commit_match:
        for line in commit_match.group(1).splitlines():
            line_clean = line.strip().lstrip("-*").strip()
            if line_clean and is_post_review_commit(line_clean, commit_patterns):
                errors.append(f"{filepath.name}: Blind prompt contains post-review fixup commit: '{line_clean}'")

    escaped = re.escape(reviewer_handle)
    desc_section_match = re.search(r"## Change Description\s*\n(.*?)(?:\n## Code Diff|\n---)", content, re.DOTALL)
    if desc_section_match:
        desc_text = desc_section_match.group(1)
        cleaned_desc = re.sub(rf"\b{escaped}/[\w\-]+", "repo", desc_text, flags=re.IGNORECASE)
        cleaned_desc = re.sub(rf"https?://[^\s]*{escaped}[^\s]*", "url", cleaned_desc, flags=re.IGNORECASE)
        if re.search(rf"\b{escaped}\b", cleaned_desc, re.IGNORECASE):
            errors.append(f"{filepath.name}: Reviewer handle '{reviewer_handle}' leaked in description/commits")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSONL files and blind prompts")
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--prompts-dir", type=Path, default=None)
    parser.add_argument("--reviewer-handle", type=str, default="pganssle")
    parser.add_argument("--check-diff-targets", action="store_true", default=True)
    parser.add_argument("--no-check-diff-targets", action="store_false", dest="check_diff_targets")
    parser.add_argument("--check-commits", action="store_true", default=True)
    parser.add_argument("--no-check-commits", action="store_false", dest="check_commits")
    args = parser.parse_args()

    commit_patterns = build_post_review_commit_patterns(args.reviewer_handle)
    has_errors = False

    for f in args.files:
        if f.suffix == ".jsonl":
            with open(f, "r", encoding="utf-8") as fp:
                errs: List[str] = []
                count = 0
                for line_no, line in enumerate(fp, start=1):
                    if not line.strip():
                        continue
                    count += 1
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        errs.append(f"{f.name}:{line_no}: Invalid JSON: {e}")
                        continue
                    errs.extend(
                        validate_record(
                            data,
                            line_no,
                            f.name,
                            commit_patterns,
                            check_diff_targets=args.check_diff_targets,
                            check_commits=args.check_commits,
                        )
                    )
                if errs:
                    has_errors = True
                    logger.error("Validation FAILED for %s (%d records, %d errors)", f.name, count, len(errs))
                    for e in errs[:10]:
                        print(f"  - {e}")
                else:
                    logger.info("Validation PASSED for %s (%d records)", f.name, count)

    if args.prompts_dir and args.prompts_dir.exists():
        prompt_files = sorted(args.prompts_dir.glob("*.md"))
        prompt_errors = 0
        for pf in prompt_files:
            errs = validate_blind_prompt(pf, args.reviewer_handle, commit_patterns)
            if errs:
                has_errors = True
                prompt_errors += len(errs)
                for e in errs:
                    print(f"  - {e}")
        if prompt_errors == 0:
            logger.info("All %d blind prompts in %s PASSED validation.", len(prompt_files), args.prompts_dir)

    if has_errors:
        sys.exit(1)
    logger.info("All validation checks PASSED successfully.")


if __name__ == "__main__":
    main()
