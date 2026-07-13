#!/usr/bin/env python3
"""Generate a detailed Mermaid import graph with edge counts and cyclic highlighting."""

import ast
from collections import Counter
from pathlib import Path

def build() -> None:
    edges = []
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                target = node.module
                if target.startswith("src.") or target in mod:
                    edges.append((mod.replace(".", "_"), target.replace(".", "_")))
    
    counts = Counter(edges)
    lines = ["```mermaid", "graph TD;"]
    for (a, b), n in counts.most_common():
        width = min(n, 5)
        lines.append(f"    {a}==>|{n}|{b};")
    # Detect simple 2-cycles
    for (a, b), n in counts.items():
        if (b, a) in counts:
            lines.append(f"    style {a} fill:#f96")
            lines.append(f"    style {b} fill:#f96")
    lines.append("```")
    Path("IMPORTS_VIZ.md").write_text("\\n".join(lines))
    print(f"✅ IMPORTS_VIZ.md ({len(edges)} edges, {len(counts)} unique).")

if __name__ == "__main__":
    build()
