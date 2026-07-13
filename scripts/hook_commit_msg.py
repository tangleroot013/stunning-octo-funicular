#!/usr/bin/env python3
"""Commit-msg hook: enforce conventional commit format and ticket reference."""

import re
import sys
from pathlib import Path

PATTERN = re.compile(r"^(feat|fix|chore|docs|refactor|test|ci|build|perf)(\(.+\))?!?: .+")

def validate() -> int:
    msg_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".git/COMMIT_EDITMSG")
    if not msg_file.exists():
        return 0
    
    lines = msg_file.read_text().splitlines()
    subject = lines[0] if lines else ""
    
    if not PATTERN.match(subject):
        print(f"❌ Commit message must follow: type(scope)?: description")
        print(f"   Got: {subject[:60]}")
        return 1
    
    # Optional: check for ticket reference
    if "#" not in subject and len(lines) > 1:
        body = "\n".join(lines[1:])
        if "#" not in body:
            print("⚠️  Consider adding a ticket reference (#123)")
    
    print(f"✅ Commit message valid: {subject[:40]}...")
    return 0

if __name__ == "__main__":
    sys.exit(validate())
