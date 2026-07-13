#!/usr/bin/env python3
"""Detect regex patterns vulnerable to catastrophic backtracking (ReDoS)."""

import ast
import re
import sys
from pathlib import Path

DANGEROUS = re.compile(r"\\(\\*|\\+|\\?|\\{.*,.*\\})[\\w\\W]*\\1")  # nested quantifiers

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        tree = ast.parse(py.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                pat = node.value
                if len(pat) > 5:
                    # Check for nested quantifiers
                    if re.search(r"\\(.*\\*|\\+|\\?\\)\\+|\\(.*\\*|\\+|\\?\\)\\*", pat):
                        if re.search(r"\\(.*\\[.*\\+.*\\]\\)", pat):  # character class with quantifier
                            print(f"🚨 {py}:{node.lineno} possible ReDoS: {pat[:60]}...")
                            hits += 1
    if hits:
        print(f"\\n❌ {hits} regex pattern(s) may be vulnerable to ReDoS.")
        return 1
    print("✅ No obvious ReDoS patterns.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
