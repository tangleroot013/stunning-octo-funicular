#!/usr/bin/env python3
"""Measure and report import chain depth to identify circular and deep imports."""

import ast
from collections import defaultdict
from pathlib import Path

def build_graph() -> dict[str, set[str]]:
    graph = defaultdict(set)
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("src.") or not "." in node.module:
                    graph[mod].add(node.module)
    return graph

def max_depth(graph: dict, start: str, visited: set = None) -> int:
    if visited is None:
        visited = set()
    if start in visited:
        return 0
    visited.add(start)
    if start not in graph or not graph[start]:
        return 1
    return 1 + max((max_depth(graph, dep, visited.copy()) for dep in graph[start]), default=1)

def report() -> None:
    graph = build_graph()
    depths = [(mod, max_depth(graph, mod)) for mod in graph]
    print("# Import Depth Analysis\n")
    for mod, d in sorted(depths, key=lambda x: -x[1])[:15]:
        bar = "→" * min(d, 10)
        print(f"  {d:2d} {bar} {mod}")

if __name__ == "__main__":
    report()
