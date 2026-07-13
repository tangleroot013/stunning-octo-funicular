#!/usr/bin/env python3
"""Detect potential IDOR vulnerabilities: user-controlled IDs in data access patterns."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if route handler
                is_route = any(
                    isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ("get", "post", "put", "delete")
                    for d in node.decorator_list
                )
                if not is_route:
                    continue
                
                # Check for user_id parameter without ownership check
                params = [a.arg for a in node.args.args]
                if any(x in params for x in ("user_id", "id", "resource_id", "item_id")):
                    has_ownership_check = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Compare):
                            if isinstance(child.ops[0], ast.Eq) if child.ops else False:
                                for comparator in [child.left] + list(child.comparators):
                                    if isinstance(comparator, ast.Attribute):
                                        if comparator.attr in ("user_id", "owner_id", "created_by"):
                                            has_ownership_check = True
                    if not has_ownership_check:
                        print(f"🚨 {py}:{node.lineno} {node.name}() — user-controlled ID without ownership verification")
                        print(f"   Add: assert resource.owner_id == current_user.id")
                        hits += 1
                    else:
                        print(f"✅ {py}:{node.lineno} {node.name}() — ownership check present")
    if hits:
        print(f"\n❌ {hits} potential IDOR vulnerability(ies). Verify authorization.")
        return 1
    print("✅ No obvious IDOR patterns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
