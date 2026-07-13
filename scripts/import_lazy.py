#!/usr/bin/env python3
"""Auto-refactor heavy top-level imports to lazy function-scoped imports."""

import ast
import sys
from pathlib import Path

HEAVY = {"pandas", "numpy", "tensorflow", "torch", "sklearn", "django", "flask", "sqlalchemy", "requests", "boto3", "pillow"}

def refactor(target: Path) -> int:
    source = target.read_text()
    tree = ast.parse(source)
    lines = source.splitlines()
    
    imports_to_move = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if any(h in node.module for h in HEAVY):
                imports_to_move.append((node.lineno - 1, node.end_lineno - 1, node.module, [a.name for a in node.names]))
    
    if not imports_to_move:
        return 0
    
    # Remove top-level imports (naive: blank them out)
    for start, end, mod, names in sorted(imports_to_move, reverse=True):
        for i in range(start, end + 1):
            lines[i] = ""
    
    # Find first function/class and inject lazy imports
    first_def = min((n.lineno - 1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))), default=0)
    inject = []
    for _, _, mod, names in imports_to_move:
        inject.append(f"    import {mod}  # lazy-loaded")
    
    lines.insert(first_def, "\n".join(inject))
    target.write_text("\n".join(lines))
    print(f"✅ {target}: moved {len(imports_to_move)} heavy import(s) to lazy scope")
    return len(imports_to_move)

def main() -> int:
    total = 0
    for py in Path("src").rglob("*.py"):
        total += refactor(py)
    print(f"\n{'✅' if total else 'ℹ️'} Refactored {total} heavy import(s) total")
    return 0

if __name__ == "__main__":
    sys.exit(main())
