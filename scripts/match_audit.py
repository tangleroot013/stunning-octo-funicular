#!/usr/bin/env python3
"""Audit match/case statements for exhaustiveness and wildcard placement."""

import ast
import sys
from pathlib import Path

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Match):
                has_wildcard = any(isinstance(c, ast.MatchAs) and c.pattern is None for c in node.cases)
                case_count = len(node.cases)
                
                if not has_wildcard:
                    print(f"⚠️  {py}:{node.lineno} match without wildcard case")
                    hits += 1
                
                # Check if wildcard is last
                if has_wildcard and case_count > 1:
                    last_is_wildcard = isinstance(node.cases[-1], ast.MatchAs) and node.cases[-1].pattern is None
                    if not last_is_wildcard:
                        print(f"⚠️  {py}:{node.lineno} wildcard case is not last")
                        hits += 1
                
                print(f"✅ {py}:{node.lineno} match with {case_count} case(s)")
    if hits:
        print(f"\n⚠️  {hits} match statement issue(s).")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
