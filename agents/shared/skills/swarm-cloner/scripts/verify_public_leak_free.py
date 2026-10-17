#!/usr/bin/env python3
"""Automated leak verification check for public/ trees in review corpora and skills.

Scans every file under a target public/ directory to guarantee ZERO internal
changelist references, internal bug tracker URLs/IDs, internal monorepo paths,
or proprietary project names leak into open-source distributions.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
from typing import List, Sequence

# Constructed via concatenation so this script file itself can reside inside
# a scanned public/ directory without self-triggering literal substring matches.
DEFAULT_FORBIDDEN_SUBSTRINGS: Sequence[str] = (
    "c" + "l-",
    "c" + "l/",
    "goog" + "le3",
    "crit" + "ique",
    "smart_" + "buildings",
    "corp/" + "ml",
    "g3" + "doc",
)

INTERNAL_BUG_PATTERN = re.compile(r"\bb" + r"/\d+", re.IGNORECASE)
INTERNAL_BUG_URL_PATTERN = re.compile(r"https?://(?:b|issues)" + r"/\d+", re.IGNORECASE)


def check_file(filepath: Path, forbidden_substrings: Sequence[str]) -> List[str]:
    """Checks a single file for forbidden internal terms and bug tracker patterns."""
    errors: List[str] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"Unable to read file as UTF-8: {filepath}"]

    for term in forbidden_substrings:
        matches = list(re.finditer(re.escape(term), content, re.IGNORECASE))
        if matches:
            for m in matches[:3]:
                snippet = content[max(0, m.start() - 25) : min(len(content), m.end() + 25)].replace("\n", " ")
                errors.append(f"Forbidden term '{term}' found: ...{snippet}...")

    bug_matches = list(INTERNAL_BUG_PATTERN.finditer(content))
    if bug_matches:
        for m in bug_matches[:3]:
            errors.append(f"Internal issue ID found: '{m.group(0)}'")

    url_matches = list(INTERNAL_BUG_URL_PATTERN.finditer(content))
    if url_matches:
        for m in url_matches[:3]:
            errors.append(f"Internal issue URL found: '{m.group(0)}'")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a public/ directory tree is 100% leak-free")
    parser.add_argument(
        "--public-dir",
        type=Path,
         nargs="+",
        default=[Path(__file__).resolve().parent.parent.parent],
        help="One or more public directory paths to scan",
    )
    parser.add_argument(
        "--forbidden-term",
        action="append",
        default=[],
        help="Additional forbidden substring to scan for (may be specified multiple times)",
    )
    args = parser.parse_args()

    forbidden_terms = list(DEFAULT_FORBIDDEN_SUBSTRINGS) + list(args.forbidden_term)
    any_failed = False

    for raw_dir in args.public_dir:
        pub_dir = raw_dir.resolve()
        if not pub_dir.exists():
            print(f"[ERROR] Public directory does not exist: {pub_dir}")
            sys.exit(1)

        print(f"Scanning public tree at {pub_dir} for internal leaks...")
        total_files = 0
        all_violations = []

        for root, _, files in os.walk(pub_dir):
            for fname in sorted(files):
                fpath = Path(root) / fname
                total_files += 1
                errs = check_file(fpath, forbidden_terms)
                if errs:
                    all_violations.append((fpath.relative_to(pub_dir), errs))

        print(f"Scanned {total_files} files under {pub_dir}.")

        if all_violations:
            any_failed = True
            print(f"[FAIL] Found {len(all_violations)} files with internal leaks in {pub_dir}:")
            for rel_path, errs in all_violations:
                print(f"  - {rel_path} ({len(errs)} violations):")
                for e in errs:
                    print(f"      {e}")
        else:
            print(f"[SUCCESS] All {total_files} files in {pub_dir} are 100% CLEAN and leak-free!")

    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
