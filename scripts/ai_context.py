#!/usr/bin/env python3
"""Build an AI context payload from src/ respecting .claudeignore and byte_budget from settings.json."""

import json
from pathlib import Path

def build() -> None:
    data = json.loads(Path("settings.json").read_text())
    budget = data.get("ai_collaboration", {}).get("byte_budget", {}).get("total_payload_limit_bytes", 1048576)
    ignore = set()
    for f in (".claudeignore", ".gitignore"):
        if Path(f).exists():
            ignore.update(line.strip() for line in Path(f).read_text().splitlines() if line.strip() and not line.startswith("#"))
    
    payload = []
    total = 0
    for py in sorted(Path("src").rglob("*.py")):
        rel = str(py.relative_to("."))
        if any(py.match(g) for g in ignore if g):
            continue
        text = py.read_text()
        if total + len(text.encode()) > budget:
            payload.append(f"# ... truncated at budget {budget} bytes\n")
            break
        payload.append(f"### {rel}\n```python\n{text}\n```\n")
        total += len(text.encode())
    
    Path("AI_CONTEXT.md").write_text("\n".join(payload))
    print(f"✅ AI_CONTEXT.md built ({total} bytes, limit {budget}).")

if __name__ == "__main__":
    build()
