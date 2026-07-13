#!/usr/bin/env python3
"""Generate a Mermaid dependency graph of internal src/ imports."""

import ast
from pathlib import Path

def build() -> None:
    edges = []
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("src.") or not "." in node.module:
                    edges.append((mod, node.module))
    lines = ["```mermaid", "graph TD;"]
    for a, b in sorted(set(edges)):
        lines.append(f"    {a.replace('.', '_')}-->{b.replace('.', '_')};")
    lines.append("```")
    Path("DEPENDENCY_GRAPH.md").write_text("\\n".join(lines))
    print(f"✅ DEPENDENCY_GRAPH.md written ({len(edges)} edges).")

if __name__ == "__main__":
    build()
