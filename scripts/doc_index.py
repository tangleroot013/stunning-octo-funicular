#!/usr/bin/env python3
"""Generate a markdown index of all public functions in src/."""

import ast
import re
from pathlib import Path

def docstrings(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node)
            items.append(f"- `{node.name}` — {doc or '*(no docstring)*'}")
    return items

def index() -> None:
    lines = ["# API Index\n"]
    for py in sorted(Path("src").rglob("*.py")):
        if items := docstrings(py):
            rel = py.relative_to("src")
            lines.append(f"## {rel}")
            lines.extend(items)
            lines.append("")
    Path("API_INDEX.md").write_text("\n".join(lines))
    print("✅ API_INDEX.md generated.")

if __name__ == "__main__":
    index()
