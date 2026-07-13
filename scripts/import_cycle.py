#!/usr/bin/env python3
"""Detect circular imports in src/ using static analysis."""

import ast
import sys
from collections import defaultdict
from pathlib import Path

def build_graph() -> dict[str, set[str]]:
    graph = defaultdict(set)
    for py in Path("src").rglob("*.py"):
        mod = ".".join(py.relative_to("src").with_suffix("").parts)
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                target = node.module
                if target.startswith("src"):
                    graph[mod].add(target)
    return graph

def dfs(node: str, graph: dict, visited: set, stack: set) -> list[str] | None:
    stack.add(node)
    for neighbor in graph.get(node, []):
        if neighbor in stack:
            return [node, neighbor]
        if neighbor not in visited:
            result = dfs(neighbor, graph, visited, stack)
            if result:
                return [node] + result
    stack.remove(node)
    visited.add(node)
    return None

def main() -> int:
    graph = build_graph()
    for mod in graph:
        cycle = dfs(mod, graph, set(), set())
        if cycle:
            print(f"🔄 Circular import: {' -> '.join(cycle)}")
            return 1
    print("✅ No circular imports detected.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
