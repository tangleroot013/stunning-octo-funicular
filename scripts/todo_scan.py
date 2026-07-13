#!/usr/bin/env python3
"""Scan src/ for TODO/FIXME/HACK comments and emit a markdown report."""

import re
from pathlib import Path

PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|XXX)[\s:]+(.+)", re.IGNORECASE)

def scan() -> None:
    lines = ["# TODO/FIXME Report\n"]
    for py in sorted(Path("src").rglob("*.py")):
        hits = []
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if m := PATTERN.search(line):
                hits.append(f"- Line {i}: **{m.group(1)}** — {m.group(2).strip()}")
        if hits:
            lines.append(f"## {py}\n")
            lines.extend(hits)
            lines.append("")
    Path("TODO_REPORT.md").write_text("\n".join(lines) or "# TODO/FIXME Report\n\n✅ Clean slate.\n")
    print("✅ TODO_REPORT.md generated.")

if __name__ == "__main__":
    scan()
