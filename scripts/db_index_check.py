#!/usr/bin/env python3
"""Detect SQL query strings missing WHERE clauses on unindexed columns."""

import ast
import re
import sys
from pathlib import Path

RISKY = re.compile(r"SELECT.*FROM.*WHERE.*\\b(id|user_id|email|uuid)\\b.*=.*\\?", re.IGNORECASE)

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                sql = node.value
                if "SELECT" in sql.upper() and "WHERE" in sql.upper():
                    if not RISKY.search(sql):
                        print(f"⚠️  {py}:{node.lineno} query may lack indexed WHERE: {sql[:60]}...")
                        hits += 1
    if hits:
        print(f"\n❌ {hits} query(s) may scan unindexed columns.")
        return 1
    print("✅ All queries appear to use indexed columns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
