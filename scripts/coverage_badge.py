#!/usr/bin/env python3
"""Inject a coverage badge into README.md based on latest pytest output."""

import re
from pathlib import Path

README = Path("README.md")
BADGE_PATTERN = re.compile(r"!\[coverage\]\([^)]+\)")

def extract_coverage() -> str | None:
    for line in Path(".coverage_report").read_text().splitlines():
        if m := re.search(r"TOTAL\s+.*?\s+(\d+)%", line):
            return m.group(1)
    return None

def update_badge(coverage: str) -> None:
    color = "brightgreen" if int(coverage) >= 85 else "yellow" if int(coverage) >= 70 else "red"
    badge = f"![coverage](https://img.shields.io/badge/coverage-{coverage}%25-{color})"
    content = README.read_text()
    if BADGE_PATTERN.search(content):
        content = BADGE_PATTERN.sub(badge, content)
    else:
        content = badge + "\n\n" + content
    README.write_text(content)
    print(f"✅ Badge updated to {coverage}%")

if __name__ == "__main__":
    if pct := extract_coverage():
        update_badge(pct)
    else:
        print("⚠️  No coverage data found. Run pytest with --cov first.")
