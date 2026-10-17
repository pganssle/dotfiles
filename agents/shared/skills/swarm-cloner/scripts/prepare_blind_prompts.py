#!/usr/bin/env python3
"""Generates clean, zero-leakage blind review prompt packets.

Reads evaluation splits (dev_eval.jsonl, blind_test_eval.jsonl) and formats
individual markdown prompt packets under splits/blind_prompts/<id>.md.

Strict Zero-Leakage Guarantee:
Prompts contain ONLY:
  - Temporal anchor (review_date) & era/technical context
  - Project/repository name & source platform
  - Change title & full description (sanitized of reviewer identity)
  - Pre-review commit messages & linked issue context
  - Pre-review unified code diff
Under NO circumstances are ground-truth comments, reviewer identity, or review
verdicts included in the prompt packets.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("prepare_blind_prompts")

PROMPT_TEMPLATE = """# Code Review Request: [{id}] {title}

**Source Platform**: {source_label}
**Project / Repository**: `{project}`
**Review Date (Temporal Anchor)**: {review_date}
**Era & Technical Context**:
{era_context}

---

## Change Description
{description}

{commit_section}
{linked_bug_section}
---

## Code Diff Under Review

```diff
{diff}
```

---

## Review Instructions for Agent
You are reviewing the proposed change above in the role of an expert senior software engineer and reviewer.
Evaluate this change thoroughly in the context of the project, language version, and temporal era specified.

Format your review with clear file and line anchors, followed by an explanation of the concern and recommended resolution.
"""


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


def sanitize_metadata_text(text: str, reviewer_handle: str) -> str:
    """Strips reviewer metadata tags and mentions of the reviewer handle to avoid bias."""
    if not text:
        return ""
    escaped = re.escape(reviewer_handle)
    lines = []
    for line in text.splitlines():
        if re.match(r"^\s*(APPROVED|R|CC|REQUIRED_REVIEW|REVIEWED_BY)\s*=", line):
            continue
        if re.search(rf"\bReporter:\s*{escaped}\b", line, flags=re.IGNORECASE):
            continue
        lines.append(line)
    cleaned = "\n".join(lines)
    cleaned = re.sub(rf"Note:\s*{escaped}\s+is\s+referenced[^\n]*\n?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(rf"@{escaped}\b", "@reviewer", cleaned, flags=re.IGNORECASE)
    return cleaned


def format_commit_section(commit_messages: Any, commit_patterns: Sequence[re.Pattern[str]]) -> str:
    if not commit_messages:
        return ""
    msgs = [commit_messages] if isinstance(commit_messages, str) else list(commit_messages)
    cleaned = []
    for msg in msgs:
        if not msg:
            continue
        msg_str = str(msg).strip()
        if not any(p.search(msg_str) for p in commit_patterns):
            cleaned.append(msg_str)
    if not cleaned:
        return ""
    lines = ["## Commit Messages"] + [f"- {m}" for m in cleaned]
    return "\n".join(lines) + "\n\n"


def format_linked_bug_section(
    bug_id: Optional[str],
    bug_context: Optional[str],
    reviewer_handle: str,
) -> str:
    if not bug_id and not bug_context:
        return ""
    out = ["## Linked Issue Context"]
    if bug_id:
        out.append(f"**Reference**: `{bug_id}`")
    if bug_context and bug_context.strip():
        cleaned = sanitize_metadata_text(bug_context.strip(), reviewer_handle)
        if cleaned.strip():
            out.append(cleaned.strip())
    return "\n\n".join(out) + "\n\n"


def generate_blind_prompt(
    record: Dict[str, Any],
    reviewer_handle: str,
    commit_patterns: Sequence[re.Pattern[str]],
) -> str:
    rec_id = record.get("id", "unknown-id")
    title = record.get("title", "Untitled change").strip()
    source = record.get("source", "github").lower()
    source_label = "Pull Request" if source == "github" else "Code Review Change"
    project = record.get("project", "unknown-project").strip()
    review_date = record.get("review_date", "Unknown date").strip()
    era_context = record.get("era_context", "Modern software development environment.").strip()
    raw_description = record.get("description", "").strip() or "*No description provided.*"
    description = sanitize_metadata_text(raw_description, reviewer_handle)
    diff = record.get("diff", "").strip()

    commit_sec = format_commit_section(record.get("commit_messages"), commit_patterns)
    bug_sec = format_linked_bug_section(
        record.get("linked_bug_id"), record.get("linked_bug_context"), reviewer_handle
    )

    return PROMPT_TEMPLATE.format(
        id=rec_id,
        title=title,
        source_label=source_label,
        project=project,
        review_date=review_date,
        era_context=era_context,
        description=description,
        commit_section=commit_sec,
        linked_bug_section=bug_sec,
        diff=diff,
    )


def process_split_file(
    split_path: Path,
    split_name: str,
    output_dir: Path,
    manifest: List[Dict[str, Any]],
    reviewer_handle: str,
    commit_patterns: Sequence[re.Pattern[str]],
) -> int:
    if not split_path.exists():
        logger.warning("Split file does not exist: %s", split_path)
        return 0

    count = 0
    with open(split_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error("Error decoding %s:%d: %s", split_path, line_no, e)
                continue

            rec_id = record.get("id")
            if not rec_id:
                continue

            safe_id = re.sub(r"[^\w\-.]", "_", str(rec_id))
            out_file = output_dir / f"{safe_id}.md"
            prompt_text = generate_blind_prompt(record, reviewer_handle, commit_patterns)
            out_file.write_text(prompt_text, encoding="utf-8")

            count += 1
            manifest.append({
                "id": rec_id,
                "split": split_name,
                "file_path": str(out_file),
                "source": record.get("source"),
                "project": record.get("project"),
                "review_date": record.get("review_date"),
                "diff_lines": len(record.get("diff", "").splitlines()),
                "ground_truth_comment_count": len(record.get("ground_truth_comments", [])),
            })

    logger.info("Generated %d blind prompts from %s (%s)", count, split_path.name, split_name)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate blind evaluation prompts from dataset splits")
    parser.add_argument("--dev-split", type=Path, default=Path("splits/dev_eval.jsonl"))
    parser.add_argument("--test-split", type=Path, default=Path("splits/blind_test_eval.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("splits/blind_prompts"))
    parser.add_argument("--reviewer-handle", type=str, default="pganssle")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest: List[Dict[str, Any]] = []
    commit_patterns = build_post_review_commit_patterns(args.reviewer_handle)

    total_dev = process_split_file(
        args.dev_split, "dev_eval", args.output_dir, manifest, args.reviewer_handle, commit_patterns
    )
    total_test = process_split_file(
        args.test_split, "blind_test_eval", args.output_dir, manifest, args.reviewer_handle, commit_patterns
    )

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Blind prompt generation complete: {total_dev} dev prompts, {total_test} blind test prompts.")


if __name__ == "__main__":
    main()
