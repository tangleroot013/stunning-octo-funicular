#!/usr/bin/env python3
"""Detect potential prompt injection vectors in LLM/AI integration code."""

import ast
import re
import sys
from pathlib import Path

INJECTION_MARKERS = [
    re.compile(r"ignore previous instructions", re.IGNORECASE),
    re.compile(r"ignore (all )?above", re.IGNORECASE),
    re.compile(r"you are now", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
    re.compile(r"DAN|jailbreak", re.IGNORECASE),
]

DANGEROUS_PATTERNS = {
    "direct_concat": re.compile(r"prompt\s*\+\s*"),
    "fstring_in_prompt": re.compile(r'f["\'].*\{.*\}.*["\']'),
    "format_in_prompt": re.compile(r'\.format\('),
}

def audit() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        tree = ast.parse(text)
        
        # Check for user input flowing into prompt variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "prompt" in target.id.lower():
                        # Check if value contains user input
                        if isinstance(node.value, (ast.BinOp, ast.JoinedStr, ast.Call)):
                            print(f"⚠️  {py}:{node.lineno} prompt built dynamically: {target.id}")
                            print(f"   Verify input sanitization before LLM call")
                            hits += 1
        
        # Check string literals for injection markers
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for marker in INJECTION_MARKERS:
                    if marker.search(node.value):
                        print(f"🚨 {py}:{node.lineno} potential injection marker in string")
                        hits += 1
        
        # Check for dangerous patterns
        for pattern_name, pat in DANGEROUS_PATTERNS.items():
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line) and "prompt" in line.lower():
                    print(f"🚨 {py}:{i} {pattern_name}: {line.strip()[:60]}")
                    hits += 1
    
    if hits:
        print(f"\n❌ {hits} potential prompt injection vector(s). Sanitize all user input.")
        return 1
    print("✅ No obvious prompt injection vectors.")
    return 0

if __name__ == "__main__":
    sys.exit(audit())
