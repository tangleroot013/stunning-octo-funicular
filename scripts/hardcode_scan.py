#!/usr/bin/env python3
"""Detect hardcoded IPs, URLs, and passwords in source files."""

import re
import sys
from pathlib import Path

PATTERNS = {
    "IP address": re.compile(r"\b(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}\b"),
    "HTTP URL": re.compile(r"https?://[^\"\\s]+"),
    "password=": re.compile(r"password\s*=\s*[\"'][^\"']+[\"']", re.IGNORECASE),
    "token=": re.compile(r"token\s*=\s*[\"'][^\"']{10,}[\"']", re.IGNORECASE),
}

def scan() -> int:
    hits = 0
    for py in Path("src").rglob("*.py"):
        text = py.read_text()
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                line = text[:m.start()].count("\\n") + 1
                snippet = m.group()[:40]
                print(f"🚨 {name} in {py}:{line} → {snippet}...")
                hits += 1
    if hits:
        print(f"\\n❌ {hits} hardcoded value(s) detected.")
        return 1
    print("✅ No hardcoded credentials or URLs detected.")
    return 0

if __name__ == "__main__":
    sys.exit(scan())
