#!/usr/bin/env python3
"""Deep-scan repo for common secret patterns."""

import re
import subprocess
from pathlib import Path

PATTERNS = {
    "GitHub PAT": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    "AWS Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Private Key": re.compile(r"-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----"),
    "Slack Token": re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
}

def scan() -> int:
    files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    hits = 0
    for f in files:
        path = Path(f)
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                print(f"🚨 {name} in {f}:{text[:m.start()].count(chr(10)) + 1}")
                hits += 1
    if hits:
        print(f"\n❌ Found {hits} potential secret(s).")
        return 1
    print("✅ No obvious secrets detected.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(scan())
