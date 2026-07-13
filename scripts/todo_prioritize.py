#!/usr/bin/env python3
"""Score TODO comments by proximity to production code and keyword severity."""

import re
from pathlib import Path

SEVERITY = {"HACK": 3, "XXX": 3, "FIXME": 2, "TODO": 1, "NOTE": 0}
PATTERN = re.compile(r"#\\s*(HACK|XXX|FIXME|TODO|NOTE)[\\s:]*(.*)", re.IGNORECASE)

def score() -> None:
    todos = []
    for py in Path("src").rglob("*.py"):
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if m := PATTERN.search(line):
                keyword = m.group(1).upper()
                text = m.group(2).strip()
                # Higher score for files closer to entry points
                depth = len(py.relative_to("src").parts)
                score = SEVERITY.get(keyword, 1) * 10 + max(0, 5 - depth) * 2
                todos.append((score, py, i, keyword, text))
    
    print("# Prioritized TODOs\n")
    for score, py, line, kw, text in sorted(todos, key=lambda x: -x[0])[:20]:
        flag = "🔥" if score >= 30 else "⚠️" if score >= 20 else "📌"
        print(f"{flag} [{score:02d}] {py}:{line} {kw}: {text[:60]}")

if __name__ == "__main__":
    score()
