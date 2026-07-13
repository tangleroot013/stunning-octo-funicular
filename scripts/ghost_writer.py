#!/usr/bin/env python3
"""Auto-generate missing Google-style docstring stubs from type hints and defaults."""

import ast
import re
from pathlib import Path

def generate(node: ast.FunctionDef) -> str:
    args = []
    for arg in node.args.args:
        name = arg.arg
        ann = ast.unparse(arg.annotation) if arg.annotation else "Any"
        default = ""
        args.append(f"    {name}: {ann}{default}")
    returns = ast.unparse(node.returns) if node.returns else "None"
    body = ['"""TODO: describe this function."""', "", "Args:", *args, "", f"Returns:\\n    {returns}"]
    return '\\n    '.join(body)

def write() -> None:
    for py in Path("src").rglob("*.py"):
        source = py.read_text()
        tree = ast.parse(source)
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node) and not node.name.startswith("_"):
                indent = "    " * (node.col_offset // 4 + 1)
                doc = generate(node)
                # Naive insertion after def line
                lines = source.splitlines()
                insert_at = node.lineno  # 1-based
                lines.insert(insert_at, indent + '"""' + doc.split('"""')[1] + '"""')
                source = "\n".join(lines)
                changed = True
                print(f"✏️  {py}:{node.name}")
        if changed:
            py.write_text(source)
    print("✅ Ghost-written docstrings inserted.")

if __name__ == "__main__":
    write()
