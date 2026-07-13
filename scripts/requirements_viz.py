#!/usr/bin/env python3
"""Generate a Mermaid graph of direct dependencies from requirements.txt."""

from pathlib import Path
import re

def viz() -> None:
    req = Path("requirements.txt")
    if not req.exists():
        print("ℹ️  No requirements.txt found.")
        return
    
    deps = []
    for line in req.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            m = re.match(r"([a-zA-Z0-9_-]+)", line)
            if m:
                deps.append(m.group(1))
    
    lines = ["```mermaid", "graph TD;"]
    for dep in deps:
        safe = dep.replace("-", "_")
        lines.append(f"    project--> {safe};")
    lines.append("```")
    
    Path("DEPENDENCIES_VIZ.md").write_text("\n".join(lines) + "\n")
    print(f"✅ DEPENDENCIES_VIZ.md ({len(deps)} direct deps)")

if __name__ == "__main__":
    viz()
